import os
import sys
import time
import platform
import subprocess
import pyperclip
from pynput.keyboard import Controller, Key
from pathlib import Path
from echo.utils.logger import get_logger
from echo.utils.notifications import NotificationManager

class InputHandler:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.keyboard = Controller()
        self.typing_delay = 0.01  # Delay between characters
        self.notifications = NotificationManager()

    def check_accessibility_permissions(self):
        """Check if app has accessibility permissions"""
        try:
            if platform.system() != 'Darwin':
                return True
                
            # Check if running as app bundle
            if getattr(sys, 'frozen', False):
                check_cmds = [
                    ['osascript', '-e', 'tell application "System Events" to tell process "Echo Assistant" to return true'],
                    ['osascript', '-e', 'tell application "System Events" to tell process "Echo" to return true']
                ]
                
                for cmd in check_cmds:
                    try:
                        result = subprocess.run(cmd, capture_output=True)
                        if result.returncode == 0:
                            return True
                    except Exception:
                        continue
                return False
            else:
                return True  # When running from source
                
        except Exception as e:
            self.logger.error(f"Error checking accessibility: {e}")
            return False
    
    def type_text(self, text):
        """Type the text character by character at current cursor position"""
        try:
            # Check permissions first
            if not self.check_accessibility_permissions():
                self.notifications.notify(
                    "Accessibility Required",
                    "Please grant accessibility permissions in System Settings → Privacy → Accessibility",
                    "⚠️",
                    sound_type='error'
                )
                return False

            # Copy to clipboard as backup
            pyperclip.copy(text)
            self.logger.info(f"Text copied to clipboard as backup: {text}")
            print(f"\n📋 Text copied to clipboard as backup")
            
            # Type each character
            print("⌨️ Typing text...")
            for char in text:
                try:
                    self.keyboard.type(char)
                    time.sleep(self.typing_delay)  # Small delay between characters
                except Exception as e:
                    self.logger.error(f"Error typing character '{char}': {e}")
                    continue
            
            self.logger.info("Text typed successfully")
            print("✅ Text typed successfully")
            print("📋 Text also available in clipboard (Cmd+V/Ctrl+V if needed)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in type_text: {e}")
            print(f"❌ Error: {e}")
            print("📋 Text copied to clipboard (manual paste required)")
            return False

    def type_with_special_chars(self, text):
        """Handle special characters and formatting"""
        special_chars = {
            '\n': Key.enter,
            '\t': Key.tab,
            ' ': Key.space
        }
        
        try:
            if not self.check_accessibility_permissions():
                self.notifications.notify(
                    "Accessibility Required",
                    "Please grant accessibility permissions in System Settings → Privacy → Accessibility",
                    "⚠️",
                    sound_type='error'
                )
                return False

            for char in text:
                if char in special_chars:
                    self.keyboard.press(special_chars[char])
                    self.keyboard.release(special_chars[char])
                else:
                    self.keyboard.type(char)
                time.sleep(self.typing_delay)
            return True
        except Exception as e:
            self.logger.error(f"Error in type_with_special_chars: {e}")
            return False