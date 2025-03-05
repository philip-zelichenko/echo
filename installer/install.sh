#!/bin/bash

        echo "🎤 Echo Assistant Installer"
        echo "=========================="

        # Check for Homebrew
        if ! command -v brew &> /dev/null; then
            echo "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            
            # Add Homebrew to PATH
            if [[ $(uname -m) == 'arm64' ]]; then
                echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
                eval "$(/opt/homebrew/bin/brew shellenv)"
            else
                echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
                eval "$(/usr/local/bin/brew shellenv)"
            fi
        fi

        # Install required dependencies
        echo "Installing dependencies..."
        brew install terminal-notifier xz

        # Kill any existing instances and clean up
        pkill -f "Echo Assistant" || true
        rm -f /tmp/echo_assistant.*
        launchctl unload ~/Library/LaunchAgents/com.echo.assistant.plist 2>/dev/null || true

        # Get OpenAI API key
        echo -n "Enter your OpenAI API key (will be hidden): "
        read -s OPENAI_API_KEY
        echo

        # Save API key to configuration
        CONFIG_DIR="$HOME/.echo_assistant"
        mkdir -p "$CONFIG_DIR"
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" > "$CONFIG_DIR/config"
        chmod 600 "$CONFIG_DIR/config"

        # Copy app to Applications
        echo "📦 Installing Echo Assistant..."
        if [ -d "/Applications/Echo Assistant.app" ]; then
            rm -rf "/Applications/Echo Assistant.app"
        fi
        cp -R "Echo Assistant.app" "/Applications/"

        # Create launch agent for login startup
        LAUNCH_AGENT="$HOME/Library/LaunchAgents/com.echo.assistant.plist"
        cat > "$LAUNCH_AGENT" << EOL
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.echo.assistant</string>
            <key>Program</key>
            <string>/Applications/Echo Assistant.app/Contents/MacOS/Echo Assistant</string>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <false/>
            <key>ProcessType</key>
            <string>Interactive</string>
            <key>StandardOutPath</key>
            <string>${HOME}/.echo_assistant/logs/echo_assistant.log</string>
            <key>StandardErrorPath</key>
            <string>${HOME}/.echo_assistant/logs/echo_assistant.error.log</string>
            <key>WorkingDirectory</key>
            <string>/Applications/Echo Assistant.app/Contents/Resources</string>
        </dict>
        </plist>
        EOL

        # Set permissions and create log directory
        chmod 644 "$LAUNCH_AGENT"
        mkdir -p "$HOME/.echo_assistant/logs"

        # Load launch agent
        launchctl unload "$LAUNCH_AGENT" 2>/dev/null || true
        launchctl load "$LAUNCH_AGENT"

        echo "✅ Installation complete!"
        echo "Echo Assistant will start automatically when you log in."
        echo "To start now, either:"
        echo "1. Double-click Echo Assistant in Applications"
        echo "2. Run: /Applications/Echo\ Assistant.app/Contents/MacOS/Echo\ Assistant"
        