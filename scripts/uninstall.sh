#!/bin/bash

# Stop the service
launchctl remove com.voiceassistant

# Remove the plist file
rm ~/Library/LaunchAgents/com.voiceassistant.plist

# Kill any running processes
pkill -f transcriber.py

echo "Voice Assistant uninstalled!"