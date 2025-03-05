import os
import shutil
import subprocess
from pathlib import Path

def create_installer():
    print("\n🔨 Creating Echo installer package...")
    
    # Build the app first
    subprocess.run(["poetry", "run", "python", "scripts/build_app.py"], check=True)
    
    # Create installer directory
    installer_dir = Path("installer")
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    installer_dir.mkdir()
    
    # Copy app to installer directory
    app_source = Path("dist/Echo.app")
    if not app_source.exists():
        print(f"\n❌ Error: App not found at {app_source}")
        print("Please ensure the build was successful.")
        return
        
    shutil.copytree(app_source, installer_dir / "Echo.app")
    
    # Create simpler install script
    install_script = '''#!/bin/bash
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
    '''
    
    with open(installer_dir / "install.sh", "w") as f:
        f.write(install_script)
    
    # Make install script executable
    os.chmod(installer_dir / "install.sh", 0o755)
    
    print("\n✅ Installer package created!")
    print("📦 Output: installer/")
    print("\nTo install:")
    print("1. cd installer")
    print("2. ./install.sh")

if __name__ == "__main__":
    create_installer()