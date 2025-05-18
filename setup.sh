#!/bin/bash

# Setup script for Music Hoster Bot

echo "========================================="
echo "    Music Hoster Bot Setup"
echo "========================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check for Git
if ! command -v git &> /dev/null; then
    echo "Git is required but not installed. Please install Git and try again."
    exit 1
fi

# Create virtual environment
echo -e "\nCreating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo -e "\nInstalling requirements..."
pip install -r requirements.txt

# Environment variables setup
echo -e "\nSetting up environment variables..."
echo -e "\nPlease provide the following information:"

read -p "Enter your Hoster Bot Token: " HOSTER_BOT_TOKEN
read -p "Enter your GitHub Token (with access to private repository): " GITHUB_TOKEN
read -p "Enter your Telegram Admin User ID: " BOT_ADMIN_ID
read -p "Enter default API ID (optional, press Enter to skip): " DEFAULT_API_ID
read -p "Enter default API Hash (optional, press Enter to skip): " DEFAULT_API_HASH
read -p "Enter default MongoDB URI (optional, press Enter to skip): " DEFAULT_MONGODB_URI

# Create .env file
echo -e "\nCreating .env file..."
cat > .env << EOL
HOSTER_BOT_TOKEN=${HOSTER_BOT_TOKEN}
GITHUB_TOKEN=${GITHUB_TOKEN}
BOT_ADMIN_ID=${BOT_ADMIN_ID}
DEFAULT_API_ID=${DEFAULT_API_ID:-12345}
DEFAULT_API_HASH=${DEFAULT_API_HASH:-your_default_api_hash}
DEFAULT_MONGO_DB_URI=${DEFAULT_MONGODB_URI:-mongodb+srv://username:password@cluster.mongodb.net/dbname}
EOL

# Create run script
echo -e "\nCreating run script..."
cat > run.sh << EOL
#!/bin/bash
source venv/bin/activate
source .env
python main.py
EOL

chmod +x run.sh

echo -e "\n========================================="
echo "Setup completed successfully!"
echo "To run the bot, use: ./run.sh"
echo "========================================="
