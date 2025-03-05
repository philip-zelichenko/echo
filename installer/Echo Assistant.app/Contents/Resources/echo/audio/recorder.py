import sounddevice as sd
import numpy as np
import threading
from echo.utils.config import config
from echo.utils.logger import get_logger

class AudioRecorder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.sample_rate = config.audio.SAMPLE_RATE
        self.channels = config.audio.CHANNELS
        self.recording = False
        self.should_stop = False
        self.stream = None
        self.stream_lock = threading.Lock()
        self.audio_buffer = []
        self.callback_fn = None  # Add this line to store the callback

    def audio_callback(self, indata, frames, time, status, callback):
        """Process audio data from the microphone"""
        if status:
            self.logger.warning(f"Audio callback status: {status}")
        
        if self.recording and not self.should_stop:
            try:
                # Convert to float32 if needed
                audio_data = indata.copy()
                if audio_data.dtype != np.float32:
                    audio_data = audio_data.astype(np.float32)
                
                # Show audio level bars
                level = np.mean(np.abs(audio_data))
                if level > 0.001:  # Lower threshold for more sensitivity
                    bars = int(level * 100)
                    print(f"\rAudio Level: {'█' * bars}{' ' * (50-min(bars, 50))}", end='', flush=True)
                    
                    # Add to buffer
                    self.audio_buffer.append(audio_data)
                
            except Exception as e:
                self.logger.error(f"Error in audio callback: {e}")

    def start(self, callback):
        """Start recording audio"""
        self.recording = True
        self.should_stop = False
        self.audio_buffer = []
        self.callback_fn = callback  # Store the callback
        
        try:
            with self.stream_lock:
                self.stream = sd.InputStream(
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    callback=lambda *args: self.audio_callback(*args, callback),
                    blocksize=int(self.sample_rate * 0.05)  # Smaller blocks for smoother updates
                )
                self.stream.start()
            
            self.logger.info("Audio recording started")
            print("\nRecording... (Press F9 to stop)")
            
            # Keep recording until stopped
            while self.recording and not self.should_stop:
                sd.sleep(10)  # Shorter sleep for more responsive updates
                
        except Exception as e:
            self.logger.error(f"Error in recording: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop recording audio"""
        self.recording = False
        self.should_stop = True
        
        with self.stream_lock:
            if self.stream is not None:
                try:
                    self.stream.stop()
                    self.stream.close()
                    self.stream = None
                    self.logger.info("Audio recording stopped")
                    
                    # Process the complete audio buffer
                    if self.audio_buffer and self.callback_fn:
                        print("\nProcessing recorded audio...")
                        complete_audio = np.concatenate(self.audio_buffer)
                        
                        # Debug audio data
                        self.logger.info(f"Audio shape: {complete_audio.shape}")
                        self.logger.info(f"Audio max value: {np.max(np.abs(complete_audio))}")
                        self.logger.info(f"Audio min value: {np.min(complete_audio)}")
                        self.logger.info(f"Audio mean value: {np.mean(np.abs(complete_audio))}")
                        
                        if np.max(np.abs(complete_audio)) > 0:
                            self.logger.info("Sending audio to transcription")
                            self.callback_fn(complete_audio)
                        else:
                            self.logger.warning("No valid audio data detected")
                    
                except Exception as e:
                    self.logger.error(f"Error closing stream: {e}")