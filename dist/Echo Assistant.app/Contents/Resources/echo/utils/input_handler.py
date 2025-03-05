import pyperclip
import time
from pynput.keyboard import Controller, Key
from echo.utils.logger import get_logger

class InputHandler:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.keyboard = Controller()
        self.typing_delay = 0.01  # Delay between characters (adjust if needed)

    def type_text(self, text):
        """Type the text character by character at current cursor position"""
        try:
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