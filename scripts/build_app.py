import PyInstaller.__main__
import os
import sys
import shutil
import subprocess
from pathlib import Path

def update_info_plist(app_path):
    info_plist_path = app_path / "Contents" / "Info.plist"
    with open(info_plist_path, 'r') as f:
        info_plist = f.read()
    
    # Add launch argument
    if "<key>LSMinimumSystemVersion</key>" in info_plist:
        info_plist = info_plist.replace(
            "<key>LSMinimumSystemVersion</key>",
            """<key>LSEnvironment</key>
            <dict>
                <key>LAUNCH_TYPE</key>
                <string>gui</string>
            </dict>
            <key>LSMinimumSystemVersion</key>"""
        )
    
    with open(info_plist_path, 'w') as f:
        f.write(info_plist)
        
def clean_everything():
    """Clean all cached files and builds"""
    print("\n🧹 Cleaning everything...")
    
    # Kill any running instances
    subprocess.run(['pkill', '-f', 'Echo'], capture_output=True)
    
    # Unload launch agent
    subprocess.run([
        'launchctl', 'unload',
        os.path.expanduser('~/Library/LaunchAgents/com.echo.plist')
    ], capture_output=True)
    
    # Remove launch agent file
    launch_agent = Path.home() / 'Library/LaunchAgents/com.echo.plist'
    if launch_agent.exists():
        launch_agent.unlink()
    
    # Remove app and config
    paths_to_remove = [
        Path("/Applications/Echo.app"),
        Path.home() / '.echo',
        Path('build'),
        Path('dist'),
        Path('installer'),
        Path('Echo.spec'),
    ]
    
    for path in paths_to_remove:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink()
    
    # Clean Python cache
    for pattern in ['*.pyc', '*.pyo', '*.pyd']:
        for file in Path().rglob(pattern):
            file.unlink()
    
    # Remove __pycache__ directories
    for cache_dir in Path().rglob('__pycache__'):
        shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Clean PyInstaller cache
    pyinstaller_cache = Path.home() / '.cache/pyinstaller'
    if pyinstaller_cache.exists():
        shutil.rmtree(pyinstaller_cache)
    
    pyinstaller_cache2 = Path.home() / '.pyinstaller'
    if pyinstaller_cache2.exists():
        shutil.rmtree(pyinstaller_cache2)
    
    print("✨ Clean complete!")

def build_app():
    """Build the macOS app"""
    app_name = "Echo"
    
    # Clean everything first
    clean_everything()
    
    print("\n🔨 Building Echo ...")
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent
        
    # App icon path - use .icns file instead of .png
    icon_path = project_root / "src" / "echo" / "assets" / "icons" / "echo.icns"  # Changed extension
            
    
    # Define PyInstaller options
    options = [
        'src/echo/main.py',
        f'--name={app_name}',
        '--onedir',
        '--windowed',
        '--noconsole',
        f'--icon={icon_path}',
        '--noconfirm',
        '--clean',
        # Add entitlements
        '--osx-bundle-identifier=com.echo.assistant',
        '--codesign-identity=-',
        '--osx-entitlements-file=entitlements.plist',
        # Add data files - make sure icons are included
        '--add-data=src/echo/assets/icons:echo/assets/icons',  # Add this line
        # Add the entire echo package
        '--add-data=src/echo:echo',
        # Add hidden imports
        '--hidden-import=numpy',
        '--hidden-import=echo.setup',
        '--hidden-import=numpy.core._dtype_ctypes',
        '--hidden-import=numpy.fft',
        '--hidden-import=echo.voice_assistant',
        '--hidden-import=echo.utils.notifications',
        '--hidden-import=echo.services.transcriber',
        '--hidden-import=echo.services.openai_service',
        '--hidden-import=av',
        '--hidden-import=av.filter',
        '--hidden-import=av.filter.graph',
        '--hidden-import=av.audio.codeccontext',
        '--hidden-import=faster_whisper',
        '--hidden-import=rumps',
        '--hidden-import=pynput',
        '--hidden-import=pyaudio',
        # Add data files
        '--add-data=src/echo/assets:echo/assets',
        '--collect-all=numpy',
        '--collect-all=av',
        '--collect-all=faster_whisper'
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    app_resources = Path(f"dist/{app_name}.app/Contents/Resources")
    if not (app_resources / "echo.icns").exists():
        shutil.copy2(icon_path, app_resources)

    # Update Info.plist with additional settings
    info_plist = Path(f"dist/{app_name}.app/Contents/Info.plist")
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>CFBundleIconFile</key>
        <string>echo.icns</string>
        <key>CFBundleIdentifier</key>
        <string>com.echo.assistant</string>
        <key>CFBundleName</key>
        <string>Echo</string>
        <key>CFBundleDisplayName</key>
        <string>Echo</string>
        <key>CFBundleExecutable</key>
        <string>Echo</string>
        <key>CFBundlePackageType</key>
        <string>APPL</string>
        <key>CFBundleShortVersionString</key>
        <string>1.0.0</string>
        <key>LSMinimumSystemVersion</key>
        <string>10.13.0</string>
        <key>NSHighResolutionCapable</key>
        <true/>
        <key>NSMicrophoneUsageDescription</key>
        <string>Echo needs microphone access to record audio for transcription.</string>
        <key>NSAppleEventsUsageDescription</key>
        <string>Echo needs accessibility access to handle keyboard shortcuts.</string>
        <key>NSAccessibilityUsageDescription</key>
        <string>Echo needs accessibility access to respond to keyboard shortcuts.</string>
        <key>LSUIElement</key>
        <true/>
        <key>LSBackgroundOnly</key>
        <false/>
        <key>NSSupportsAutomaticGraphicsSwitching</key>
        <true/>
    </dict>
    </plist>'''
    
    with open(info_plist, 'w') as f:
        f.write(plist_content)

    # Copy icon file to Resources
    resources_dir = Path(f"dist/{app_name}.app/Contents/Resources")
    shutil.copy2(icon_path, resources_dir / "echo.icns")

    print("\n✅ Build complete!")
    print(f"📦 Output: dist/{app_name}.app")
        
if __name__ == "__main__":
    build_app()