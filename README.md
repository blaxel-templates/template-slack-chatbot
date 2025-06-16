# Blaxel Slack Agent

<p align="center">
  <img src="https://blaxel.ai/logo.png" alt="Blaxel" width="200"/>
</p>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Slack API](https://img.shields.io/badge/Slack_API-powered-brightgreen.svg)](https://api.slack.com/)
[![UV](https://img.shields.io/badge/UV-package_manager-blue.svg)](https://github.com/astral-sh/uv)

</div>

A powerful conversational agent that integrates seamlessly with Slack workspaces. This agent demonstrates advanced AI capabilities for building interactive Slack bots with tool integration, conversation management, and intelligent response generation.

## 📑 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Slack Setup](#slack-setup)
- [Usage](#usage)
  - [Running Locally](#running-the-server-locally)
  - [Testing](#testing-your-agent)
      - [Deployment](#deploying-to-blaxel)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## ✨ Features

- **Slack Integration**: Native Slack bot with real-time message handling
- **Intelligent Conversations**: Advanced AI-powered responses and context awareness
- **Tool Integration**: Support for external APIs, databases, and services
- **Event Handling**: Responds to mentions, direct messages, and slash commands
- **Streaming Responses**: Real-time message updates for better user experience
- **Multi-workspace Support**: Deploy across multiple Slack workspaces
- **Secure Authentication**: OAuth 2.0 and secure token management
- **Easy Deployment**: Seamless integration with Blaxel platform

## 🚀 Quick Start

For those who want to get up and running quickly:

```bash
# Clone the repository
git clone https://github.com/blaxel-templates/slack-agent.git

# Navigate to the project directory
cd slack-agent

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your Slack credentials

# Start the server
bl serve --hotreload

# In another terminal, test the agent
bl chat --local slack-agent
```

## 📋 Prerequisites

- **Python:** 3.10 or later
- **[UV](https://github.com/astral-sh/uv):** An extremely fast Python package and project manager, written in Rust
- **Slack Workspace:** Admin access to create and configure Slack apps
- **Blaxel Platform Setup:** Complete Blaxel setup by following the [quickstart guide](https://docs.blaxel.ai/Get-started#quickstart)
  - **[Blaxel CLI](https://docs.blaxel.ai/Get-started):** Ensure you have the Blaxel CLI installed. If not, install it globally:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/blaxel-templates/toolkit/main/install.sh | BINDIR=/usr/local/bin sudo -E sh
    ```
  - **Blaxel login:** Login to Blaxel platform
    ```bash
    bl login YOUR-WORKSPACE
    ```

## 💻 Installation

**Clone the repository and install dependencies:**

```bash
git clone https://github.com/blaxel-templates/slack-agent.git
cd slack-agent
uv sync
```

## 🔧 Slack Setup

Before running your Slack agent, you need to set up a Slack app and configure the necessary permissions:

### 1. Create a Slack App

1. Go to [Slack API Apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app and select your workspace
4. Click "Create App"

### 2. Configure Bot Permissions

Navigate to "OAuth & Permissions" and add these Bot Token Scopes:
- `app_mentions:read` - View messages that directly mention your bot
- `channels:history` - View messages in public channels
- `channels:read` - View basic information about public channels
- `chat:write` - Send messages as your bot
- `groups:history` - View messages in private channels (if needed)
- `im:history` - View messages in direct messages with your bot
- `im:read` - View basic information about direct messages
- `im:write` - Start direct messages with people

### 3. Install App to Workspace

1. In "OAuth & Permissions", click "Install to Workspace"
2. Review permissions and click "Allow"
3. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 4. Configure Event Subscriptions

1. Go to "Event Subscriptions" and enable events
2. Set Request URL to: `https://your-domain.com/slack/events`
3. Subscribe to these bot events:
   - `app_mention` - When your bot is mentioned
   - `message.channels` - Messages in channels
   - `message.im` - Direct messages

### 5. Environment Configuration

Create a `.env` file with your Slack credentials:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token (for Socket Mode, optional)
```

For detailed Slack setup instructions, visit the [Slack API Documentation](https://api.slack.com/start/building).

## 🔧 Usage

### Running the Server Locally

Start the development server with hot reloading:

```bash
bl serve --hotreload
```

_Note:_ This command starts the server and enables hot reload so that changes to the source code are automatically reflected.

### Testing your agent

You can test your agent using the chat interface:

```bash
bl chat --local slack-agent
```

Or run it directly with specific input:

```bash
bl run agent slack-agent --local --data '{"inputs": "Hello from Slack!"}'
```

### Testing in Slack

1. Invite your bot to a channel: `/invite @your-bot-name`
2. Mention your bot: `@your-bot-name Hello!`
3. Send a direct message to your bot
4. Use slash commands (if configured)

### Deploying to Blaxel

When you are ready to deploy your application:

```bash
bl deploy
```

This command uses your code and the configuration files under the `.blaxel` directory to deploy your application.

## 📁 Project Structure

- **src/main.py** - Application entry point
- **src/agent.py** - Core Slack agent implementation
- **src/slack/** - Slack-specific functionality
  - **bot.py** - Slack bot initialization and event handling
  - **handlers.py** - Message and event handlers
  - **utils.py** - Slack utility functions
- **src/server/** - Server implementation and routing
  - **router.py** - API route definitions
  - **middleware.py** - Request/response middleware
- **pyproject.toml** - UV package manager configuration
- **blaxel.toml** - Blaxel deployment configuration
- **.env.example** - Environment variables template

## ⚙️ Configuration

### Environment Variables

- `SLACK_BOT_TOKEN` - Your Slack bot token (required)
- `SLACK_SIGNING_SECRET` - Slack signing secret for request verification (required)

### Blaxel Configuration

Edit `blaxel.toml` to customize:
- Model settings and preferences
- Function definitions and tools
- Deployment environment variables
- Resource allocation

## ❓ Troubleshooting

### Common Issues

1. **Slack Authentication Issues**:
   - Verify your bot token starts with `xoxb-`
   - Check that your app is installed in the workspace
   - Ensure signing secret matches your Slack app settings

2. **Permission Errors**:
   - Verify bot has required OAuth scopes
   - Check that bot is invited to channels where it should respond
   - Ensure event subscriptions are properly configured

3. **Event Handling Problems**:
   - Confirm your Request URL is accessible and returns 200
   - Check that event subscriptions match your handler functions
   - Verify Slack can reach your webhook endpoint

 4. **Blaxel Platform Issues**:
   - Ensure you're logged in to your workspace: `bl login MY-WORKSPACE`
   - Verify models are available: `bl get models`
   - Check that functions exist: `bl get functions`

5. **Bot Response Issues**:
   - Check message formatting and Slack API limits
   - Verify conversation context and state management
   - Monitor rate limiting and API quotas

6. **Deployment and Configuration**:
   - Check environment variable configuration
   - Verify webhook URLs are publicly accessible
   - Review network connectivity and firewall settings

For more help, please [submit an issue](https://github.com/blaxel-templates/slack-agent/issues) on GitHub.

## 👥 Contributing

Contributions are welcome! Here's how you can contribute:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Submit** a Pull Request

Please make sure to update tests as appropriate and follow the code style of the project.

## 🆘 Support

If you need help with this template:

- [Submit an issue](https://github.com/blaxel-templates/slack-agent/issues) for bug reports or feature requests
- Visit the [Blaxel Documentation](https://docs.blaxel.ai) for platform guidance
- Check the [Slack API Documentation](https://api.slack.com/) for Slack-specific help
- Join our [Discord Community](https://discord.gg/G3NqzUPcHP) for real-time assistance

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
