# Music Hoster Bot - Setup Instructions

This document provides instructions for setting up and running the Music Hoster Bot.

## Prerequisites

- Python 3.8 or higher
- Git
- A Telegram Bot Token (for the Hoster Bot)
- A GitHub Token with access to the private repository
- A Telegram Admin User ID

## Environment Variables

Before running the bot, you need to set the following environment variables:

```bash
# Required variables
export HOSTER_BOT_TOKEN="your_hoster_bot_token"
export GITHUB_TOKEN="your_github_token"
export BOT_ADMIN_ID="your_telegram_user_id"

# Optional default values (can be customized)
export DEFAULT_API_ID="your_default_api_id"
export DEFAULT_API_HASH="your_default_api_hash"
export DEFAULT_MONGO_DB_URI="your_default_mongodb_uri"
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/MesteriousPrivate/MHost.git
   cd MHost
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

## Usage

Once the bot is running, users can interact with it through the following commands:

- `/start` - Start the bot and get the welcome message
- `/host` or `/clone` - Start the process of hosting a music bot
- `/stop` - Stop the currently hosted music bot
- `/status` - Check the status of the hosted bot
- `/help` - Display the help message

## Hosting Process

When a user sends the `/host` or `/clone` command, the bot will:

1. Ask for Telegram API ID (optional)
2. Ask for API Hash (optional)
3. Ask for MongoDB URI (optional)
4. Ask for Bot Token (required)
5. Ask for Log Group ID (required)
6. Ask for String Session (required)
7. Ask for Owner ID (optional)
8. Ask for Start Image URL (optional)

After collecting all the required information, the bot will clone the repository, install dependencies, and start the music bot.

## Important Notes

- Each user can only host one bot at a time
- The admin user (defined by BOT_ADMIN_ID) can stop all hosted bots by stopping their own bot
- The bot requires sufficient disk space to clone repositories for each user
- Make sure the bot has the necessary permissions to create directories and run processes

## Troubleshooting

If you encounter any issues:

1. Check the logs for error messages
2. Verify that all required environment variables are set correctly
3. Make sure the GitHub token has access to the private repository
4. Ensure that the system has enough resources to run multiple bot instances
