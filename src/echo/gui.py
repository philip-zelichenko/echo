import os
import sys
from pathlib import Path
import rumps

class EchoGUI(rumps.App):
    def __init__(self, voice_assistant=None):
        # Get the app resources path
        if getattr(sys, 'frozen', False):
            resources_path = Path(sys._MEIPASS) / "echo" / "assets" / "icons" / "echo.png"
        else:
            resources_path = Path(__file__).parent / "assets" / "icons" / "echo.png"
            
        super().__init__("Echo", icon=str(resources_path))
        
        self.voice_assistant = voice_assistant
        
        # Add keyboard shortcut menu items with callbacks
        self.menu = [
            rumps.MenuItem("Record (F9)", callback=self.handle_f9),
            rumps.MenuItem("Toggle Tone (F6)", callback=self.handle_f6),
            rumps.MenuItem("Cycle Mode (F7)", callback=self.handle_f7),
            rumps.MenuItem("Status (F8)", callback=self.handle_f8),
            None,  # separator
            rumps.MenuItem("About"),
            rumps.MenuItem("Quit")
        ]

    def set_voice_assistant(self, assistant):
        self.voice_assistant = assistant

    def handle_f9(self, sender):
        if self.voice_assistant:
            if not self.voice_assistant.is_recording:
                self.voice_assistant.start_recording()
            else:
                self.voice_assistant.stop_recording()

    def handle_f6(self, sender):
        if self.voice_assistant:
            self.voice_assistant.toggle_tone()

    def handle_f7(self, sender):
        if self.voice_assistant:
            self.voice_assistant.cycle_comm_type()

    def handle_f8(self, sender):
        if self.voice_assistant:
            self.voice_assistant.show_status()