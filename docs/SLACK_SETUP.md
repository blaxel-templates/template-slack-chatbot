# Slack Integration Setup Guide

## Overview

Your agent can now receive messages from Slack channels and respond back automatically! Here's how to set it up.

## Step 1: Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Give your app a name (e.g., "AI Assistant")
5. Select your Slack workspace

## Step 2: Configure Bot Permissions

1. In your app settings, go to "OAuth & Permissions"
2. Under "Scopes" → "Bot Token Scopes", add these permissions:
   - `chat:write` - Send messages
   - `chat:write.public` - Send messages to channels the bot hasn't joined
   - `channels:read` - View basic info about public channels
   - `groups:read` - View basic info about private channels
   - `im:read` - View basic info about direct messages
   - `mpim:read` - View basic info about group messages
   - `users:read` - View people in the workspace

## Step 3: Install the App

1. Scroll up to "OAuth Tokens for Your Workspace"
2. Click "Install to Workspace"
3. Authorize the app
4. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

## Step 4: Configure Event Subscriptions

1. Go to "Event Subscriptions" in your app settings
2. Turn on "Enable Events"
3. Set the Request URL to: `https://your-domain.com/slack/events`
   - Replace `your-domain.com` with your actual server URL
   - Slack will verify this URL, so make sure your server is running
4. Under "Subscribe to bot events", add:
   - `message.channels` - Listen to messages in channels
   - `message.groups` - Listen to messages in private channels
   - `message.im` - Listen to direct messages
   - `message.mpim` - Listen to group direct messages

## Step 5: Set Environment Variables

Create a `.env` file in your project root with:

```bash
# Slack Bot Token (from Step 3)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Signing Secret for production security
SLACK_SIGNING_SECRET=your-signing-secret-here

# Your server port
BL_SERVER_PORT=1338
```

## Step 6: Invite Bot to Channels

1. Go to the Slack channel where you want the bot to respond
2. Type: `/invite @YourBotName`
3. The bot will now listen and respond to messages in that channel

## Step 7: Test the Integration

1. Start your server:
   ```bash
   bl serve --hotreload
   ```

2. Check the integration status:
   ```bash
   curl http://localhost:80/slack/status
   ```

3. Send a message in the Slack channel where you invited the bot
4. The bot should respond automatically!

## How It Works

### Message Flow:
1. **User sends message** in Slack channel
2. **Slack sends webhook** to your `/slack/events` endpoint
3. **Your agent processes** the message using Google ADK
4. **Bot responds** back to the same channel

### Key Features:
- ✅ Responds to channel messages
- ✅ Responds to direct messages
- ✅ Maintains conversation context per user/channel
- ✅ Avoids responding to its own messages
- ✅ Error handling and logging
- ✅ Manual message sending endpoint for testing

### API Endpoints:
- `POST /slack/events` - Receives Slack events
- `POST /slack/send` - Manual message sending (for testing)
- `GET /slack/status` - Check integration status

## Testing Manually

You can test sending messages manually:

```bash
curl -X POST http://localhost:80/slack/send \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#general",
    "message": "Hello from the AI assistant!"
  }'
```

## Troubleshooting

### Bot not responding?
1. Check that `SLACK_BOT_TOKEN` is set correctly
2. Verify the bot is invited to the channel
3. Check server logs for errors
4. Ensure your webhook URL is accessible to Slack

### URL verification failed?
1. Make sure your server is running and accessible
2. Check that the `/slack/events` endpoint is working
3. Verify your server URL is correct in Slack settings

### Permission errors?
1. Review the bot permissions in OAuth & Permissions
2. Reinstall the app to workspace if you added new permissions

## Security Notes

For production:
- Use HTTPS for your webhook URL
- Implement request signature verification using `SLACK_SIGNING_SECRET`
- Store tokens securely (environment variables, not in code)
- Consider rate limiting to prevent abuse

## Next Steps

- Customize the bot's responses in `src/agent.py`
- Add more sophisticated conversation handling
- Implement slash commands for specific actions
- Add rich message formatting with Slack Block Kit