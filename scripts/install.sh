#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Check for .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo -e "${YELLOW}Please create .env file from .env.example and add your OpenAI API key${NC}"
    exit 1
fi

# Get OpenAI API key from .env
OPENAI_API_KEY=$(grep OPENAI_API_KEY "$PROJECT_DIR/.env" | cut -d '=' -f2)

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not found in .env file${NC}"
    echo -e "${YELLOW}Please add your OpenAI API key to .env file${NC}"
    exit 1
fi

# Create necessary directories
mkdir -p ~/Library/LaunchAgents
mkdir -p ~/Library/Logs/voiceassistant

# Copy and configure the plist file
cp "$PROJECT_DIR/service/com.voiceassistant.plist" ~/Library/LaunchAgents/
sed -i '' "s|PROJECT_PATH|$PROJECT_DIR|g" ~/Library/LaunchAgents/com.voiceassistant.plist
sed -i '' "s|YOUR_API_KEY|$OPENAI_API_KEY|g" ~/Library/LaunchAgents/com.voiceassistant.plist
sed -i '' "s|YOUR_USERNAME|$USER|g" ~/Library/LaunchAgents/com.voiceassistant.plist

# Set correct permissions
chmod 644 ~/Library/LaunchAgents/com.voiceassistant.plist

# Stop any existing processes
pkill -f "Echo" 2>/dev/null
launchctl remove com.voiceassistant 2>/dev/null

# Load the LaunchAgent for auto-start on login
launchctl load ~/Library/LaunchAgents/com.voiceassistant.plist

echo -e "${GREEN}Voice Assistant installed successfully!${NC}"
echo -e "${YELLOW}The app will start automatically when you log in.${NC}"
echo -e "${YELLOW}You can also start it manually:${NC}"
echo -e "  • Double-click the app icon in Applications"
echo -e "  • Or run: /Applications/Echo.app/Contents/MacOS/Echo\\ Assistant"
echo -e "${YELLOW}Check logs at: ~/Library/Logs/voiceassistant.log${NC}"