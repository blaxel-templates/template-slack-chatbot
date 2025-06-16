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
3. Set the Request URL to: `https://run.blaxel.ai/YOUR-WORKSPACE/agents/slack-agent/slack/events`
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
```

## Step 6: Invite Bot to Channels

1. Go to the Slack channel where you want the bot to respond
2. Type: `/invite @YourBotName`
3. The bot will now listen and respond to messages in that channel

## Test locally

To test your Slack integration locally during development, you'll need to expose your local server to the internet so Slack can send webhooks to it. The easiest way to do this is with ngrok.

### Step 1: Install ngrok

1. Download ngrok from [https://ngrok.com/download](https://ngrok.com/download)
2. Extract and install it according to your OS instructions
3. Sign up for a free ngrok account and get your auth token
4. Configure ngrok: `ngrok config add-authtoken YOUR_AUTH_TOKEN`

### Step 2: Start Your Local Server

```bash
bl serve --hotreload
```

### Step 3: Expose Local Server with ngrok

In a new terminal, run:
```bash
ngrok http 1338
```

You'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:1338
```

### Step 4: Update Slack App Configuration

1. Go to your Slack app settings at [https://api.slack.com/apps](https://api.slack.com/apps)
2. Navigate to "Event Subscriptions"
3. Update the Request URL to: `https://YOUR_NGROK_URL.ngrok.io/slack/events`
   - Replace `YOUR_NGROK_URL` with the actual ngrok URL (e.g., `abc123`)
4. Click "Save Changes"
5. Slack will verify the URL - make sure your local server is running!

### Step 5: Test the Integration

1. Go to a Slack channel where your bot is invited
2. Send a message
3. Check your local server logs to see the incoming webhook
4. Your bot should respond in the channel

### Important Notes for Local Testing:

- **Keep ngrok running**: If you restart ngrok, you'll get a new URL and need to update Slack again
- **Free ngrok limitations**: Free accounts get random URLs that change on restart
- **Development workflow**:
  ```bash
  # Terminal 1: Start your server
  python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Terminal 2: Start ngrok
  ngrok http 8000
  ```
- **Logs**: Monitor your local server logs to debug webhook processing
- **Remember to redeploy**: When you're done testing locally, deploy your changes with `bl deploy` and update the Slack webhook URL back to your production endpoint

### Troubleshooting Local Testing:

- **ngrok URL not working?** Make sure your local server is running on the correct port
- **Slack can't verify URL?** Check that your `/slack/events` endpoint is responding correctly
- **Messages not being received?** Verify the ngrok URL is correctly set in Slack Event Subscriptions
- **CORS issues?** Make sure your local server accepts requests from external sources


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

## Troubleshooting

### Agent is not deployed
1. Be sure to execute `bl deploy`
2. Check on https://app.blaxel.ai that your agent is well deployed

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