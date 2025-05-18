import os
import sys
import asyncio
import logging
import re
import subprocess
import shutil
import json
from datetime import datetime
from typing import Dict, Optional, Union

import telegram
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from pyrogram import Client

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_API_ID = "12345"  # Replace with your default API ID
DEFAULT_API_HASH = "your_default_api_hash"  # Replace with your default API hash
DEFAULT_MONGO_DB_URI = "mongodb+srv://username:password@cluster.mongodb.net/dbname"  # Replace with your default MongoDB URI
GITHUB_TOKEN = "your_github_token"  # Replace with your GitHub token

# Active bots storage
active_bots = {}  # user_id: {process, bot_username, token}

# States for conversation handling
class UserState:
    WAITING_API_ID = 1
    WAITING_API_HASH = 2
    WAITING_MONGO_DB = 3
    WAITING_BOT_TOKEN = 4
    WAITING_LOG_GROUP = 5
    WAITING_STRING_SESSION = 6
    WAITING_OWNER_ID = 7
    WAITING_START_IMG = 8

# User data storage
user_states = {}
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"👋 Hi {user.mention_html()}!\n\n"
        f"I am a Music Bot Hoster. I can help you host your own music bot on Heroku.\n\n"
        f"Use /host to start hosting your bot.\n"
        f"Use /clone to clone and host from GitHub."
    )

async def host_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the hosting process."""
    user_id = update.effective_user.id
    
    # Check if user already has a bot hosted
    if user_id in active_bots:
        await update.message.reply_text(
            "You already have an active bot. Please use /stop to stop it before hosting a new one."
        )
        return
    
    # Initialize user data
    user_data[user_id] = {}
    user_states[user_id] = UserState.WAITING_API_ID
    
    await update.message.reply_text(
        "Let's set up your Music Bot!\n\n"
        "Please provide your Telegram API ID or type 'None' to use the default value."
    )

async def clone_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clone and host the bot."""
    # This is the same as host_command for our implementation
    await host_command(update, context)

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop the user's hosted bot."""
    user_id = update.effective_user.id
    
    if user_id not in active_bots:
        await update.message.reply_text("You don't have any active bots to stop.")
        return
    
    try:
        # Kill the bot process
        bot_info = active_bots[user_id]
        if 'process' in bot_info and bot_info['process']:
            bot_info['process'].terminate()
            bot_info['process'].wait()
        
        # Remove the bot directory
        bot_dir = f"bots/{user_id}"
        if os.path.exists(bot_dir):
            shutil.rmtree(bot_dir)
        
        # Notify user
        await update.message.reply_text(
            f"Your bot @{bot_info.get('username', 'Unknown')} has been stopped and removed."
        )
        
        # Remove from active bots
        del active_bots[user_id]
        
        # Stop all bots if the command was issued by the main admin
        if user_id == int(os.environ.get("BOT_ADMIN_ID", "0")):
            await stop_all_bots(update)
            
    except Exception as e:
        logger.error(f"Error stopping bot: {e}")
        await update.message.reply_text(f"Error stopping bot: {str(e)}")

async def stop_all_bots(update: Update) -> None:
    """Stop all active bots."""
    for user_id, bot_info in list(active_bots.items()):
        try:
            if 'process' in bot_info and bot_info['process']:
                bot_info['process'].terminate()
                bot_info['process'].wait()
            
            bot_dir = f"bots/{user_id}"
            if os.path.exists(bot_dir):
                shutil.rmtree(bot_dir)
                
            # Don't send messages to other users to avoid spam
        except Exception as e:
            logger.error(f"Error stopping bot for user {user_id}: {e}")
    
    active_bots.clear()
    await update.message.reply_text("All bots have been stopped.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages based on the current state."""
    user_id = update.effective_user.id
    
    if user_id not in user_states:
        return
    
    message_text = update.message.text
    current_state = user_states[user_id]
    
    # Process the message based on the current state
    if current_state == UserState.WAITING_API_ID:
        if message_text.lower() == 'none':
            user_data[user_id]['api_id'] = DEFAULT_API_ID
        else:
            # Validate API ID (should be numeric)
            if not message_text.isdigit():
                await update.message.reply_text("API ID should be a numeric value. Please try again or type 'None'.")
                return
            user_data[user_id]['api_id'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_API_HASH
        await update.message.reply_text(
            "Great! Now please provide your API Hash or type 'None' to use the default value."
        )
    
    elif current_state == UserState.WAITING_API_HASH:
        if message_text.lower() == 'none':
            user_data[user_id]['api_hash'] = DEFAULT_API_HASH
        else:
            user_data[user_id]['api_hash'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_MONGO_DB
        await update.message.reply_text(
            "Now please provide your MongoDB URI or type 'None' to use the default value."
        )
    
    elif current_state == UserState.WAITING_MONGO_DB:
        if message_text.lower() == 'none':
            user_data[user_id]['mongo_db'] = DEFAULT_MONGO_DB_URI
        else:
            user_data[user_id]['mongo_db'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_BOT_TOKEN
        await update.message.reply_text(
            "Now please provide your Bot Token (this is required)."
        )
    
    elif current_state == UserState.WAITING_BOT_TOKEN:
        # Validate bot token format
        if not re.match(r'^\d+:[A-Za-z0-9_-]+$', message_text):
            await update.message.reply_text("That doesn't look like a valid bot token. Please try again.")
            return
        
        user_data[user_id]['bot_token'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_LOG_GROUP
        await update.message.reply_text(
            "Now please provide your Log Group ID (this is required).\n"
            "Note: Your bot must be in this group, the VC must always be on, "
            "and the bot must be an admin in the group."
        )
    
    elif current_state == UserState.WAITING_LOG_GROUP:
        # Validate group ID (should be numeric, possibly with a - prefix)
        if not re.match(r'^-?\d+$', message_text):
            await update.message.reply_text("That doesn't look like a valid group ID. Please try again.")
            return
        
        user_data[user_id]['log_group_id'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_STRING_SESSION
        await update.message.reply_text(
            "Now please provide your Pyrogram String Session (this is required)."
        )
    
    elif current_state == UserState.WAITING_STRING_SESSION:
        user_data[user_id]['string_session'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_OWNER_ID
        await update.message.reply_text(
            "Now please provide your Owner ID or type 'None' to skip."
        )
    
    elif current_state == UserState.WAITING_OWNER_ID:
        if message_text.lower() == 'none':
            user_data[user_id]['owner_id'] = str(user_id)  # Default to the current user
        else:
            # Validate owner ID (should be numeric)
            if not message_text.isdigit():
                await update.message.reply_text("Owner ID should be a numeric value. Please try again or type 'None'.")
                return
            user_data[user_id]['owner_id'] = message_text
        
        # Move to next state
        user_states[user_id] = UserState.WAITING_START_IMG
        await update.message.reply_text(
            "Finally, please provide a URL for your Start Image or type 'None' to use the default."
        )
    
    elif current_state == UserState.WAITING_START_IMG:
        if message_text.lower() == 'none':
            user_data[user_id]['start_img_url'] = ""  # Default empty
        else:
            # Basic URL validation
            if not message_text.startswith(('http://', 'https://')):
                await update.message.reply_text("That doesn't look like a valid URL. Please try again or type 'None'.")
                return
            user_data[user_id]['start_img_url'] = message_text
        
        # All data collected, proceed to hosting
        await update.message.reply_text("All information collected! Setting up your bot now...")
        await setup_and_start_bot(update, user_id)
        
        # Clear state
        del user_states[user_id]

async def setup_and_start_bot(update: Update, user_id: int) -> None:
    """Set up and start the music bot based on collected data."""
    try:
        # Send status update
        status_msg = await update.message.reply_text("Starting setup process...")
        
        # Create a directory for this user's bot
        bot_dir = f"bots/{user_id}"
        if os.path.exists(bot_dir):
            shutil.rmtree(bot_dir)
        os.makedirs(bot_dir, exist_ok=True)
        
        # Clone the repository
        await status_msg.edit_text("Cloning repository from GitHub...")
        await clone_repository(bot_dir)
        
        # Create the .env file with user data
        await status_msg.edit_text("Creating environment configuration...")
        env_data = user_data[user_id]
        create_env_file(bot_dir, env_data)
        
        # Install requirements
        await status_msg.edit_text("Installing requirements... This might take a few minutes.")
        await install_requirements(bot_dir)
        
        # Start the bot
        await status_msg.edit_text("Starting your music bot...")
        process = start_bot_process(bot_dir)
        
        # Get bot information
        bot_token = env_data['bot_token']
        bot_username = await get_bot_username(bot_token)
        
        # Store active bot information
        active_bots[user_id] = {
            'process': process,
            'token': bot_token,
            'username': bot_username
        }
        
        # Notify user
        await status_msg.edit_text(
            f"🎉 Your bot @{bot_username} has been successfully started!\n\n"
            f"You can now start using your Music Bot."
        )
        
    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        await update.message.reply_text(f"❌ Error setting up bot: {str(e)}")
        
        # Clean up on failure
        bot_dir = f"bots/{user_id}"
        if os.path.exists(bot_dir):
            shutil.rmtree(bot_dir)

async def install_requirements(bot_dir: str) -> None:
    """Install requirements from requirements.txt."""
    process = subprocess.Popen(
        ["pip", "install", "-r", "requirements.txt"],
        cwd=bot_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Failed to install requirements: {stderr.decode()}")
        
async def clone_repository(bot_dir: str) -> None:
    """Clone the GitHub repository to the specified directory."""
    repo_url = f"https://{GITHUB_TOKEN}@github.com/MesteriousPrivate/ShrutiMusic.git"
    
    # Clone the repository
    process = subprocess.Popen(
        ["git", "clone", repo_url, bot_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"Failed to clone repository: {stderr.decode()}")

def create_env_file(bot_dir: str, env_data: Dict[str, str]) -> None:
    """Create .env file with user configuration."""
    env_content = [
        f"API_ID={env_data['api_id']}",
        f"API_HASH={env_data['api_hash']}",
        f"BOT_TOKEN={env_data['bot_token']}",
        f"MONGO_DB_URI={env_data['mongo_db']}",
        f"LOG_GROUP_ID={env_data['log_group_id']}",
        f"STRING_SESSION={env_data['string_session']}",
        f"OWNER_ID={env_data['owner_id']}",
    ]
    
    if env_data.get('start_img_url'):
        env_content.append(f"START_IMG_URL={env_data['start_img_url']}")
    
    with open(f"{bot_dir}/.env", "w") as f:
        f.write("\n".join(env_content))

def start_bot_process(bot_dir: str) -> subprocess.Popen:
    """Start the bot process."""
    # Use bash start script from the repository
    process = subprocess.Popen(
        ["bash", "start"],
        cwd=bot_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    return process

async def get_bot_username(token: str) -> str:
    """Get the username of the bot using its token."""
    bot = telegram.Bot(token)
    bot_info = await bot.get_me()
    return bot_info.username

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show status of the user's hosted bot."""
    user_id = update.effective_user.id
    
    if user_id not in active_bots:
        await update.message.reply_text("You don't have any active bots.")
        return
    
    bot_info = active_bots[user_id]
    await update.message.reply_text(
        f"Your bot @{bot_info.get('username', 'Unknown')} is currently active."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message with available commands."""
    help_text = (
        "🤖 *Music Bot Hoster Help* 🤖\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot and get welcome message\n"
        "/host - Host a new music bot\n"
        "/clone - Same as /host, clones and hosts the bot\n"
        "/stop - Stop your currently hosted bot\n"
        "/status - Check status of your hosted bot\n"
        "/help - Show this help message\n\n"
        "*Hosting Process:*\n"
        "1. You'll be asked for API ID (optional)\n"
        "2. API Hash (optional)\n"
        "3. MongoDB URI (optional)\n"
        "4. Bot Token (required)\n"
        "5. Log Group ID (required)\n"
        "6. String Session (required)\n"
        "7. Owner ID (optional)\n"
        "8. Start Image URL (optional)\n\n"
        "*Notes:*\n"
        "- For optional fields, you can type 'None' to use defaults\n"
        "- Your bot must be in the log group with admin rights\n"
        "- Voice chat must be on in the log group\n"
        "- Each user can host only one bot at a time"
    )
    
    await update.message.reply_markdown(help_text)

def main() -> None:
    """Start the bot."""
    # Create necessary directories
    os.makedirs("bots", exist_ok=True)
    
    # Get the bot token from environment variables
    token = os.environ.get("HOSTER_BOT_TOKEN")
    if not token:
        logger.error("No bot token provided. Please set the HOSTER_BOT_TOKEN environment variable.")
        sys.exit(1)
    
    # Create application and add handlers
    application = ApplicationBuilder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("host", host_command))
    application.add_handler(CommandHandler("clone", clone_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add message handler for collecting data
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Starting Music Hoster Bot...")
    application.run_polling()

if __name__ == "__main__":
    # Check for required environment variables
    missing_vars = []
    for var in ["HOSTER_BOT_TOKEN", "GITHUB_TOKEN", "BOT_ADMIN_ID"]:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these environment variables before running the bot.")
        sys.exit(1)
    
    # Update global variables from environment
    GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
    
    main()
