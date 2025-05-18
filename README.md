# 🎵 Shruti Music Hoster Bot 🎵

![Shruti Music Hoster](https://envs.sh/r2J.jpg)

A powerful Telegram bot to host your own music bot with ease! This bot allows users to deploy their own music bots without any technical knowledge - just provide the necessary tokens and information, and your bot will be ready in minutes!

## 🌟 Features

- **One-Command Deployment**: Deploy music bots with a simple command
- **Customizable**: Set your own API credentials, MongoDB URI, and more
- **User-Friendly**: Interactive step-by-step setup process
- **Multiple Bot Support**: Each user can host their own music bot
- **Admin Controls**: Admin can control all active bots
- **Status Updates**: Check the status of your hosted bot anytime
- **Easy Management**: Start and stop your bot with simple commands

## 📋 Requirements

- Python 3.8 or higher
- Telegram Bot Token
- GitHub Access Token
- [Optional] Custom API ID/Hash
- [Optional] MongoDB URI
- [Optional] Custom start image URL

## 🚀 Quick Start

1. Talk to [@HostMusicrobot](http://t.me/HostMusicrobot) on Telegram
2. Use `/host` or `/clone` command to start the setup process
3. Follow the instructions to provide your bot token and other information
4. Wait for the bot to set up everything for you
5. Start using your music bot!

## 📝 Available Commands

- `/start` - Start interaction with the bot
- `/host` or `/clone` - Begin hosting your music bot
- `/stop` - Stop your currently hosted bot
- `/status` - Check the status of your hosted bot
- `/help` - Show help information

## 📌 Setup Process

When you use the `/host` or `/clone` command, the bot will ask you for:

1. **API ID** (optional) - Your Telegram API ID or type 'None' to use default
2. **API Hash** (optional) - Your Telegram API Hash or type 'None' to use default
3. **MongoDB URI** (optional) - Your MongoDB connection string or type 'None' to use default
4. **Bot Token** (required) - The token for your music bot (get it from [@BotFather](http://t.me/BotFather))
5. **Log Group ID** (required) - ID of the group where bot logs will be sent
   - Your bot must be admin in this group
   - Voice chat must always be on in this group
6. **String Session** (required) - Pyrogram string session for authentication
7. **Owner ID** (optional) - Your Telegram user ID or type 'None' to use default
8. **Start Image URL** (optional) - URL for the bot's start image or type 'None' to use default

## 📚 Important Notes

- Each user can host only one bot at a time
- The bot will be deployed using the [ShrutiMusic](https://github.com/MesteriousPrivate/ShrutiMusic) repository
- You must keep the host bot running for your music bot to work
- If the main admin stops their bot, all other hosted bots will also stop

## 🔧 Advanced Setup (For Self-Hosting)

If you want to host the Hoster Bot yourself:

1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Set up environment variables:
   ```
   HOSTER_BOT_TOKEN=your_hoster_bot_token
   GITHUB_TOKEN=your_github_token
   BOT_ADMIN_ID=your_telegram_user_id
   DEFAULT_API_ID=your_default_api_id
   DEFAULT_API_HASH=your_default_api_hash
   DEFAULT_MONGO_DB_URI=your_default_mongodb_uri
   ```
4. Run the bot: `python main.py`

## 🔍 Troubleshooting

- **Bot not starting**: Make sure your bot token is valid
- **Clone failed**: Check if the GitHub token has proper permissions
- **Connection issues**: Ensure your string session is correct and not expired
- **Log group errors**: Verify the bot is admin in the log group and VC is on

## 📢 Support and Updates

- **Support Group**: [@ShrutiBotSupport](https://t.me/ShrutiBotSupport)
- **Updates Channel**: [@ShrutiBots](https://t.me/ShrutiBots)
- **Owner**: [@WTF_WhyMeeh](https://t.me/WTF_WhyMeeh)
- **Hoster Bot**: [@HostMusicrobot](http://t.me/HostMusicrobot)

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💖 Credits

- [ShrutiMusic](https://github.com/MesteriousPrivate/ShrutiMusic) - The music bot repository
- [@WTF_WhyMeeh](https://t.me/WTF_WhyMeeh) - Developer and Maintainer
- All contributors and supporters of the project

## ⚠️ Disclaimer

This bot is for educational and personal use only. Please ensure you comply with Telegram's Terms of Service and API usage policies.
