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
    subprocess.run(['pkill', '-f', 'Echo Assistant'], capture_output=True)
    
    # Unload launch agent
    subprocess.run([
        'launchctl', 'unload',
        os.path.expanduser('~/Library/LaunchAgents/com.echo.assistant.plist')
    ], capture_output=True)
    
    # Remove launch agent file
    launch_agent = Path.home() / 'Library/LaunchAgents/com.echo.assistant.plist'
    if launch_agent.exists():
        launch_agent.unlink()
    
    # Remove app and config
    paths_to_remove = [
        Path("/Applications/Echo Assistant.app"),
        Path.home() / '.echo_assistant',
        Path('build'),
        Path('dist'),
        Path('installer'),
        Path('Echo Assistant.spec'),
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
    """Build the Echo Assistant app"""
    # Clean everything first
    clean_everything()
    
    print("\n🔨 Building Echo Assistant...")
    
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent
        
    # App icon path
    icon_path = project_root / "src" / "echo" / "assets" / "icons" / "echo.png"
    
    # Get path to faster-whisper assets
    import faster_whisper
    whisper_path = Path(faster_whisper.__file__).parent
    assets_path = whisper_path / "assets"
    print(f"Including Whisper assets from: {assets_path}")
    
    # Define PyInstaller options
    options = [
        'src/echo/main.py',
        '--name=Echo Assistant',
        '--onedir',
        '--windowed',
        f'--icon={icon_path}',
        '--noconfirm',
        '--clean',
        # Add hidden imports
        '--hidden-import=numpy',
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
        # Add data files
        '--add-data=src/echo:echo',
        '--collect-all=numpy',
        '--collect-all=av',
        '--collect-all=faster_whisper'
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(options)
    
    print("\n✅ Build complete!")
    print("📦 Output: dist/Echo Assistant.app")

if __name__ == "__main__":
    build_app()