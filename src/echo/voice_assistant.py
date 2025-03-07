import os
import sys
import time
import rumps
import threading
import subprocess
from pynput import keyboard

from echo.audio.recorder import AudioRecorder
from echo.services.transcription import Transcriber
from echo.services.openai_service import OpenAIService
from echo.utils.sounds import play_start_sound, play_stop_sound
from echo.utils.logger import get_logger
from echo.utils.input_handler import InputHandler
from echo.utils.config import ToneMode, CommunicationType
from echo.utils.notifications import NotificationManager



class VoiceAssistant:
    def __init__(self, gui=None):
        self.logger = get_logger(__name__)
        self.logger.info("Initializing Voice Assistant...")

        self.gui = gui
        self.recorder = AudioRecorder()
        self.transcription = Transcriber()
        self.openai = OpenAIService()
        self.input_handler = InputHandler()
        self.recording_thread = None
        self.is_recording = False
        self.running = True
        self.notifications = NotificationManager()

        self.current_tone = ToneMode.FRIENDLY
        self.current_comm_type = CommunicationType.DM
    
        # Initialize keyboard listener but don't start it yet
        self.keyboard_listener = None
        self.keyboard_initialized = False

    def start_keyboard_listener(self):
        """Start the keyboard listener"""
        if self.keyboard_initialized:
            return
            
        try:
            # Always set up pynput listener
            from pynput import keyboard
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release,
                suppress=False
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            
            # If we're running as bundled app, also set up rumps callbacks
            if getattr(sys, 'frozen', False) and self.gui:
                menu_items = self.gui._menu.values()
                for item in menu_items:
                    if isinstance(item, rumps.MenuItem):
                        if "F9" in item.title:
                            item.callback = self._handle_f9
                        elif "F6" in item.title:
                            item.callback = self._handle_f6
                        elif "F7" in item.title:
                            item.callback = self._handle_f7
                        elif "F8" in item.title:
                            item.callback = self._handle_f8
            
            self.keyboard_initialized = True
            return True
                
        except Exception as e:
            self.logger.error(f"Error starting keyboard listener: {e}")
            return False
                            
    def _handle_f9(self, sender):
        """Handle F9 shortcut via rumps"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def _handle_f6(self, sender):
        """Handle F6 shortcut via rumps"""
        self.toggle_tone()

    def _handle_f7(self, sender):
        """Handle F7 shortcut via rumps"""
        self.cycle_comm_type()

    def _handle_f8(self, sender):
        """Handle F8 shortcut via rumps"""
        self.show_status()
                    
    def show_status(self):
        """Display current settings and send notification"""
        # Terminal display
        print("\n" + "="*50)
        print("Current Settings:")
        
        # Get tone info
        tone_display = "😊 Friendly" if self.current_tone == ToneMode.FRIENDLY else "🎯 Business"
        print(f"Tone    : {tone_display}")
        
        # Get mode info
        mode_emojis = {
            CommunicationType.EMAIL: "📧",
            CommunicationType.DM: "💬",
            CommunicationType.SOCIAL: "📱",
            CommunicationType.NOTES: "📝"
        }
        mode_emoji = mode_emojis.get(self.current_comm_type, "")
        mode_name = self.current_comm_type.value.replace('_', ' ').title()
        print(f"Mode    : {mode_emoji} {mode_name}")
        print("="*50 + "\n")
        
        # Send notification with current status
        status_message = f"Tone: {tone_display}\nMode: {mode_emoji} {mode_name}"
        self.notifications.notify(
            "Current Status",
            status_message,
            "ℹ️"  # Info emoji
        )

    def toggle_tone(self):
        """Toggle between friendly and business tone"""
        if self.current_tone == ToneMode.FRIENDLY:
            self.current_tone = ToneMode.BUSINESS
            self.notifications.notify("Tone Changed", "Switched to Business tone", "🎯")
        else:
            self.current_tone = ToneMode.FRIENDLY
            self.notifications.notify("Tone Changed", "Switched to Friendly tone", "😊")
        self.show_status()

    def cycle_comm_type(self):
        """Cycle through communication types"""
        types = list(CommunicationType)
        current_index = types.index(self.current_comm_type)
        next_index = (current_index + 1) % len(types)
        self.current_comm_type = types[next_index]
        
        mode_emojis = {
            CommunicationType.EMAIL: "📧",
            CommunicationType.DM: "💬",
            CommunicationType.SOCIAL: "📱",
            CommunicationType.NOTES: "📝"
        }
        
        self.notifications.notify(
            "Mode Changed", 
            f"Switched to {self.current_comm_type.value.replace('_', ' ').title()} mode",
            mode_emojis[self.current_comm_type]
        )
        self.show_status()
        
    def process_audio(self, audio_data):
        """Process audio data in real-time"""
        try:
            print("\nProcessing complete audio...")
            self.logger.debug("Processing complete audio...")
            
            # Process with transcription service
            print("Calling transcribe_audio...")
            text = self.transcription.transcribe_audio(audio_data)
            print(f"Got transcription: {text}")
            
            if text and text.strip():
                print(f"\nTranscribed: {text}")
                self.logger.info(f"Transcribed: {text}")
                
                # Get OpenAI response
                print("Getting OpenAI response...")
                self.openai.initialize()
                response_text, processing_time = self.openai.process_text(
                    text, 
                    tone=self.current_tone,
                    comm_type=self.current_comm_type
                )

                if response_text:
                    print(f"\n🤖 Assistant: {response_text}")
                    print(f"⏱️ Processing time: {processing_time:.2f}s")
                    
                    # Type the processed text
                    print("\nTyping response...")
                    if self.input_handler.type_text(response_text):
                        print("✅ Response typed successfully")
                    else:
                        print("❌ Failed to type response")
                
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}", exc_info=True)
            print(f"\nError: {e}")
            
    def start_recording(self):
        """Start recording audio"""
        self.notifications.notify(
            "Recording", 
            "Started recording...", 
            "🎤"
        )

        if not self.is_recording:
            self.is_recording = True
            play_start_sound()
            self.logger.info("Recording started")
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(
                target=self.recorder.start,
                args=(self.process_audio,)
            )
            self.recording_thread.daemon = True  # Make thread daemon so it stops when main thread stops
            self.recording_thread.start()

    def stop_recording(self):
        """Stop recording audio"""
        self.notifications.notify(
            "Processing", 
            "Processing recording...", 
            "⚙️"
        )

        if self.is_recording:
            self.is_recording = False
            self.recorder.should_stop = True
            
            if self.recording_thread:
                self.recording_thread.join()
                self.recording_thread = None  # Clear the thread reference
            
            play_stop_sound()
            self.logger.info("Recording stopped")

    def on_press(self, key):
        """Handle keyboard shortcuts"""
        try:
            self.logger.debug(f"Key pressed: {key}")
            # Only handle our specific shortcuts
            if key in [keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8, keyboard.Key.f9]:
                if key == keyboard.Key.f9:
                    if not self.is_recording:
                        self.start_recording()
                    else:
                        self.stop_recording()
                elif key == keyboard.Key.f6:
                    self.toggle_tone()
                elif key == keyboard.Key.f7:
                    self.cycle_comm_type()
                elif key == keyboard.Key.f8:
                    self.show_status()
                        
        except Exception as e:
            self.logger.error(f"Error handling key press: {e}")

    def on_release(self, key):
        """Handle key release events"""
        try:
            self.logger.debug(f"Key released: {key}")
        except Exception as e:
            self.logger.error(f"Error in key release handler: {e}")

    def check_microphone_permissions(self):
        """Check microphone access by attempting to open a test stream"""
        try:
            import pyaudio
            
            # Try to initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Try to get default input device info
            try:
                device_info = audio.get_default_input_device_info()
                self.logger.info(f"Found input device: {device_info['name']}")
            except IOError:
                self.notifications.notify(
                    "Microphone Access Required",
                    "Please enable microphone access in System Settings → Privacy → Microphone",
                    "⚠️"
                )
                return False
                
            # Try to open a test stream
            try:
                stream = audio.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024,
                    start=False
                )
                stream.close()
            except Exception as e:
                self.logger.error(f"Error opening audio stream: {e}")
                self.notifications.notify(
                    "Microphone Access Required",
                    "Please enable microphone access in System Settings → Privacy → Microphone",
                    "⚠️"
                )
                return False
                
            finally:
                audio.terminate()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking microphone: {e}")
            return False

    def run(self):
        """Run the voice assistant"""
        try:
            # Check microphone permissions first
            if not self.check_microphone_permissions():
                self.logger.error("Microphone access not available")
                return

            # Try to start keyboard listener
            keyboard_ok = self.start_keyboard_listener()
            
            if keyboard_ok:
                msg = "Ready! Press F9 to start recording."
            else:
                msg = "Running in limited mode. Please grant accessibility permissions."
                
            self.notifications.notify(
                "Voice Assistant",
                msg,
                "🎤",
                sound_type='startup'
            )
            
            print(f"\nVoice Assistant ready! {msg}")
            
            while self.running:
                time.sleep(0.1)
                    
        except Exception as e:
            self.logger.error(f"Error in voice assistant: {e}")
        finally:
            self.cleanup()
                                    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.is_recording:
            self.stop_recording()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        self.logger.info("Voice Assistant shutting down...")