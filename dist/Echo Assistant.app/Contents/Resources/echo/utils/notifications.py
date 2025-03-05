import os
import platform
import subprocess
from pathlib import Path
from echo.utils.logger import get_logger

class NotificationManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_mac = platform.system() == 'Darwin'
        
        self.sounds = {
            'startup': 'Funk',     # System startup
            'mode': 'Submarine',   # Mode changes
            'tone': 'Submarine',   # Tone changes
            'record': 'Blow',      # Start recording
            'success': 'Bottle',   # Success events
            'error': 'Sosumi'      # Error events
        }
        
        # Initialize without icon path
        self.icon_path = None
        
        # Get the absolute path to the project root
        project_root = Path(__file__).parent.parent
        
        # Try to find icon in various locations
        possible_paths = [
            # Check in app bundle first
            Path("/Applications/Echo Assistant.app/Contents/Resources/echo/assets/icons/echo.png"),
            # Then check development paths
            Path(__file__).parent.parent / "assets" / "icons" / "echo.png",
            Path(__file__).parent.parent.parent / "assets" / "icons" / "echo.png"
        ]
        
        for path in possible_paths:
            try:
                if path.exists():
                    self.icon_path = str(path)
                    break
            except Exception as e:
                self.logger.error(f"Error finding icon: {e}")
                self.icon_path = "com.apple.Safari"
                
        self.terminal_notifier_paths = [
            '/usr/local/bin/terminal-notifier',
            '/opt/homebrew/bin/terminal-notifier',
            '/usr/bin/terminal-notifier'
        ]
        
        self.terminal_notifier = None
        if self.is_mac:
            self.find_terminal_notifier()

    def find_terminal_notifier(self):
        """Find terminal-notifier in known locations"""
        # First check if it's in PATH
        try:
            result = subprocess.run(['which', 'terminal-notifier'], 
                                capture_output=True, text=True)
            if result.returncode == 0:
                self.terminal_notifier = result.stdout.strip()
                return
        except Exception:
            pass
        
        # Check known locations
        for path in self.terminal_notifier_paths:
            if os.path.exists(path):
                self.terminal_notifier = path
                return

    def notify(self, title, message, emoji="", sound_type='mode'):
        """Send notification"""
        try:
            if not self.is_mac:
                print(f"\n{emoji} {title}: {message}")
                return

            # If no terminal-notifier found, just print
            if not self.terminal_notifier:
                print(f"\n{emoji} {title}: {message}")
                return

            # Only try once to send notification
            try:
                cmd = [
                    self.terminal_notifier,
                    '-title', f'{emoji} {title}',
                    '-message', message,
                    '-sound', self.sounds.get(sound_type, 'Pop')
                ]
                
                subprocess.run(cmd, capture_output=True, timeout=1)
            except Exception as e:
                self.logger.error(f"Failed to send notification: {e}")
                print(f"\n{emoji} {title}: {message}")
                
        except Exception as e:
            self.logger.error(f"Notification error: {e}")
            print(f"\n{emoji} {title}: {message}")