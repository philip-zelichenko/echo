import os
import sys
import time
import platform
import subprocess
from pathlib import Path
from echo.utils.logger import get_logger
from echo.utils.notifications import NotificationManager

class PermissionsManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.notifications = NotificationManager()

    def check_all_permissions(self):
        """Check both microphone and accessibility permissions"""
        mic_ok = self.check_microphone_permissions()
        access_ok = self.check_accessibility_permissions()
        
        if not (mic_ok and access_ok):
            # Open System Settings to Privacy & Security
            subprocess.run([
                "open",
                "x-apple.systempreferences:com.apple.preference.security"
            ])
            
            self.notifications.notify(
                "Echo",
                "Please grant both Microphone and Accessibility permissions",
                "⚠️"
            )
            
            # Show detailed instructions
            print("\n⚙️ Permission Setup Required:")
            print("1. In System Settings → Privacy & Security:")
            print("   • Enable Microphone access for Echo")
            print("   • Enable Accessibility access for Echo")
            print("2. Restart Echo after granting permissions\n")
            
            return False
        return True

    def check_microphone_permissions(self):
        """Check microphone permissions"""
        try:
            import sounddevice as sd
            sd.query_devices()
            return True
        except Exception as e:
            self.logger.error(f"Microphone access error: {e}")
            return False

    def check_accessibility_permissions(self):
        """Check accessibility permissions"""
        try:
            if platform.system() != 'Darwin':
                return True
                
            # Force a permission prompt by attempting to use accessibility
            try:
                subprocess.run([
                    'osascript',
                    '-e',
                    'tell application "System Events" to keystroke "x" using {command down}'
                ], capture_output=True, check=True)
                return True
            except subprocess.CalledProcessError:
                return False
                
        except Exception as e:
            self.logger.error(f"Accessibility check error: {e}")
            return False 