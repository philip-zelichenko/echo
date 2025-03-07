#!/usr/bin/env python3
"""
Echo Voice Assistant Installer
This script handles the complete installation of Echo on macOS.
"""

import os
import sys
import subprocess
from pathlib import Path
import platform

def run_command(command, description=None):
    """Run a shell command and print its output"""
    if description:
        print(f"\n📝 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.output:
            print(e.output)
        return False

def check_prereqs():
    """Check and install prerequisites"""
    if platform.system() != "Darwin":
        print("❌ This installer only works on macOS")
        sys.exit(1)

    # Check/Install Homebrew
    if not run_command("which brew", "Checking for Homebrew"):
        print("\n🍺 Installing Homebrew...")
        if not run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'):
            print("❌ Failed to install Homebrew")
            sys.exit(1)

    # Check/Install Python
    if not run_command("which python3", "Checking for Python"):
        print("\n🐍 Installing Python...")
        if not run_command("brew install python@3.11"):
            print("❌ Failed to install Python")
            sys.exit(1)

    # Check/Install Poetry
    if not run_command("which poetry", "Checking for Poetry"):
        print("\n📝 Installing Poetry...")
        if not run_command('curl -sSL https://install.python-poetry.org | python3 -'):
            print("❌ Failed to install Poetry")
            sys.exit(1)

def setup_environment():
    """Set up the environment and dependencies"""
    # Create project directory
    project_dir = Path.home() / "echo"
    project_dir.mkdir(exist_ok=True)
    os.chdir(project_dir)

    # Clone repository
    if not (project_dir / ".git").exists():
        print("\n📦 Cloning Echo repository...")
        if not run_command("git clone https://github.com/yourusername/echo.git ."):
            print("❌ Failed to clone repository")
            sys.exit(1)

    # Get OpenAI API key
    api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
    if not api_key:
        print("❌ API key is required")
        sys.exit(1)

    # Create .env file
    with open(".env", "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")

def build_and_install():
    """Build and install the app"""
    commands = [
        ("poetry install", "Installing dependencies"),
        ("poetry run python scripts/build_app.py", "Building app"),
        ("poetry run python scripts/create_installer.py", "Creating installer"),
        ("cd installer && ./install.sh", "Installing Echo")
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"❌ Failed during: {desc}")
            sys.exit(1)

def main():
    """Main installation process"""
    print("\n🎤 Echo Voice Assistant Installer")
    print("================================")

    try:
        check_prereqs()
        setup_environment()
        build_and_install()

        print("\n✅ Installation complete!")
        print("\n📱 Usage:")
        print("1. Find Echo in your menu bar")
        print("2. Use these shortcuts:")
        print("   - F9: Start/Stop recording")
        print("   - F6: Toggle tone")
        print("   - F7: Cycle mode")
        print("   - F8: Show status")
        print("\n⚙️ If shortcuts don't work:")
        print("1. Open System Settings → Privacy & Security → Accessibility")
        print("2. Enable Echo")
        print("\n🎙️ If microphone doesn't work:")
        print("1. Open System Settings → Privacy & Security → Microphone")
        print("2. Enable Echo")

    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 