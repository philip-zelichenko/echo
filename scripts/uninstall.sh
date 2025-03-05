#!/bin/bash

echo "🗑️  Uninstalling Echo..."

# Kill all running instances
pkill -f "Echo" || true

# Unload and remove launch agents
launchctl unload ~/Library/LaunchAgents/com.echo.plist 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.voiceassistant.plist 2>/dev/null || true
rm -f ~/Library/LaunchAgents/com.echo.plist
rm -f ~/Library/LaunchAgents/com.voiceassistant.plist

# Remove app from Applications
rm -rf "/Applications/Echo.app"
rm -rf "/Applications/Echo Assistant.app"

# Remove config and logs
rm -rf ~/.echo
rm -rf ~/Library/Logs/voiceassistant*

# Remove temp files
rm -f /tmp/echo.*
rm -f /tmp/echo_assistant.*

echo "✅ Echo has been uninstalled"