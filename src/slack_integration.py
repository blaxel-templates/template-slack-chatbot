import asyncio
import os
from logging import getLogger
from typing import Any, Dict

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .agent import agent

logger = getLogger(__name__)


class SlackIntegration:
    def __init__(self):
        # Get Slack bot token from environment variable
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        if not self.bot_token:
            logger.warning("SLACK_BOT_TOKEN not found in environment variables")
            self.client = None
            self.bot_user_id = None
        else:
            self.client = WebClient(token=self.bot_token)
            logger.info("Slack WebClient initialized")
            # Get bot user ID to avoid responding to own messages
            try:
                auth_response = self.client.auth_test()
                self.bot_user_id = auth_response["user_id"]
                logger.info(f"Bot user ID: {self.bot_user_id}")
            except Exception as e:
                logger.error(f"Failed to get bot user ID: {e}")
                self.bot_user_id = None

        # Track processed messages to avoid duplicates
        self.processed_messages = set()

    async def handle_slack_event(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Handle incoming Slack events"""

        # Handle URL verification challenge
        if event_data.get("type") == "url_verification":
            return {"challenge": event_data.get("challenge")}

        # Handle actual events
        if event_data.get("type") == "event_callback":
            event = event_data.get("event", {})

            # Debug logging for all events
            logger.debug(
                f"📥 Received event: type={event.get('type')}, "
                f"subtype={event.get('subtype')}, "
                f"user={event.get('user')}, "
                f"bot_id={event.get('bot_id')}, "
                f"channel={event.get('channel')}, "
                f"ts={event.get('ts')}"
            )

            # Only respond to messages (not bot messages to avoid loops)
            if (
                event.get("type") == "message"
                and not event.get("bot_id")
                and not event.get("subtype")  # Ignore message subtypes (edits, deletes, etc.)
                and event.get("text")
                and event.get("user") != self.bot_user_id
            ):  # Don't respond to our own messages
                # Create unique message ID for deduplication
                message_id = f"{event.get('channel')}_{event.get('ts')}"

                # Check if we've already processed this message
                if message_id not in self.processed_messages:
                    self.processed_messages.add(message_id)

                    # Clean up old message IDs (keep only last 1000)
                    if len(self.processed_messages) > 1000:
                        # Remove oldest 100 entries
                        old_messages = list(self.processed_messages)[:100]
                        for old_msg in old_messages:
                            self.processed_messages.discard(old_msg)

                    await self._process_message(event)
                else:
                    logger.info(f"Skipping duplicate message: {message_id}")

        return {"status": "ok"}

    async def _process_message(self, message_event: Dict[str, Any]):
        """Process a message from Slack and respond"""
        if not self.client:
            logger.error("Slack client not initialized - missing SLACK_BOT_TOKEN")
            return

        try:
            # Extract message details
            channel = message_event.get("channel")
            user = message_event.get("user")
            text = message_event.get("text", "").strip()
            ts = message_event.get("ts")  # timestamp, can be used as session_id and thread_ts

            # Skip empty messages
            if not text:
                logger.info(f"Skipping empty message from user {user}")
                return

            # Check if this is a direct message
            is_dm = await self._is_direct_message(channel)

            if is_dm:
                logger.info(f"🤖 Processing DM from user {user}: '{text}'")
                await self._send_slack_message(channel, "Our agent is processing your message...")
            else:
                logger.info(f"🤖 Processing message from user {user} in channel {channel}: '{text}'")
                await self._send_slack_message(channel, "Our agent is processing your message...", thread_ts=ts)

            # Generate response using your agent
            response_parts = []
            async for response_chunk in agent(input=text, user_id=user, session_id=f"slack_{channel}_{user}"):
                response_parts.append(response_chunk)

            # Combine all response chunks
            full_response = "".join(response_parts).strip()

            if full_response:
                if is_dm:
                    # Send response back to DM (no threading in DMs)
                    await self._send_slack_message(channel, full_response)
                    msg = f"✅ Sent DM response to user {user}: '{full_response[:100]}"
                    if len(full_response) > 100:
                        msg += "..."
                    msg += "'"
                    logger.info(msg)
                else:
                    # Send response back to Slack in thread
                    await self._send_slack_message(channel, full_response, thread_ts=ts)
                    msg = f"✅ Sent response to thread in channel {channel}: '{full_response[:100]}"
                    if len(full_response) > 100:
                        msg += "..."
                    msg += "'"
                    logger.info(msg)
            else:
                logger.warning(f"Agent returned empty response for message: '{text}'")

        except Exception as e:
            logger.error(f"❌ Error processing Slack message: {e}")
            # Send error message to channel if possible
            if self.client and message_event.get("channel"):
                try:
                    channel = message_event["channel"]
                    is_dm = await self._is_direct_message(channel)

                    if is_dm:
                        await self._send_slack_message(
                            channel, "Sorry, I encountered an error processing your message. Please try again."
                        )
                    else:
                        await self._send_slack_message(
                            channel,
                            "Sorry, I encountered an error processing your message. Please try again.",
                            thread_ts=message_event.get("ts"),
                        )
                except Exception as send_error:
                    logger.error(f"Failed to send error message: {send_error}")

    async def _is_direct_message(self, channel_id: str) -> bool:
        """Check if a channel is a direct message"""
        try:
            # Run the blocking Slack API call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.conversations_info(channel=channel_id))

            # DMs have channel type 'im' (instant message)
            channel_info = response.get("channel", {})
            return channel_info.get("is_im", False)

        except SlackApiError as e:
            logger.error(f"Error checking channel type: {e.response['error']}")
            # If we can't determine, assume it's not a DM to be safe
            return False

    async def _send_slack_message(self, channel: str, text: str, thread_ts: str = None):
        """Send a message to a Slack channel, optionally in a thread"""
        try:
            # Run the blocking Slack API call in a thread pool
            loop = asyncio.get_event_loop()

            # Prepare message parameters
            message_params = {
                "channel": channel,
                "text": text,
                "username": "AI Assistant",
                "icon_emoji": ":robot_face:",
            }

            # Add thread_ts if provided to reply in thread
            if thread_ts:
                message_params["thread_ts"] = thread_ts

            response = await loop.run_in_executor(None, lambda: self.client.chat_postMessage(**message_params))
            return response

        except SlackApiError as e:
            logger.error(f"Error sending Slack message: {e.response['error']}")
            raise

    async def send_direct_message(self, user_id: str, message: str):
        """Send a direct message to a user"""
        if not self.client:
            logger.error("Slack client not initialized")
            return None

        try:
            # Open a DM channel with the user
            loop = asyncio.get_event_loop()
            dm_response = await loop.run_in_executor(None, lambda: self.client.conversations_open(users=user_id))

            channel_id = dm_response["channel"]["id"]

            # Send the message
            return await self._send_slack_message(channel_id, message)

        except SlackApiError as e:
            logger.error(f"Error sending DM: {e.response['error']}")
            return None


# Create global instance
slack_integration = SlackIntegration()
