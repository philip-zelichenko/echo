#!/bin/bash
        echo "🎤 Echo Installer"
        echo "=========================="

        # Kill any existing instances
        pkill -f "Echo" || true
        
        # Copy app to Applications
        echo "📦 Installing Echo..."
        if [ -d "/Applications/Echo.app" ]; then
            rm -rf "/Applications/Echo.app"
        fi
        cp -R "Echo.app" "/Applications/"

        # Request permissions
        echo "🔐 Requesting permissions..."
        tccutil reset All com.echo.app
        open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
        open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"

        echo "✅ Installation complete!"
        echo "🚀 Launch Echo from your Applications folder"
    