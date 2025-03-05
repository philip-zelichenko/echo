import sounddevice as sd
import numpy as np
import threading
import pyaudio
from echo.utils.config import config
from echo.utils.logger import get_logger

class AudioRecorder:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.sample_rate = config.audio.SAMPLE_RATE
        self.channels = config.audio.CHANNELS
        self.chunk_size = config.audio.CHUNK_SIZE
        self.recording = False
        self.should_stop = False
        self.stream = None
        self.stream_lock = threading.Lock()
        self.audio_buffer = []
        self.frames = []
        self.callback_fn = None  # Add this line to store the callback

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        try:
            if status:
                self.logger.warning(f"Audio callback status: {status}")
                
            if self.is_recording:
                # Convert to numpy array to check audio levels
                audio_data = np.frombuffer(in_data, dtype=np.float32)
                level = np.abs(audio_data).mean()
                if level > 0.001:  # Log when audio is detected
                    self.logger.info(f"Audio level: {level:.4f}")
                self.frames.append(in_data)
                
            return (in_data, pyaudio.paContinue)
            
        except Exception as e:
            self.logger.error(f"Error in audio callback: {e}")
            return (None, pyaudio.paComplete)

    def start(self, callback):
        """Start recording audio"""
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Find the right input device
            device_count = self.audio.get_host_api_info_by_index(0).get('deviceCount')
            input_device_index = None
            
            for i in range(device_count):
                device_info = self.audio.get_device_info_by_index(i)
                self.logger.info(f"Found audio device: {device_info['name']}")
                
                if (device_info.get('maxInputChannels') > 0 and
                    not device_info['name'].startswith('_') and
                    'Built-in' in device_info['name']):
                    input_device_index = i
                    self.logger.info(f"Selected input device: {device_info['name']}")
                    break
            
            if input_device_index is None:
                # Fallback to default device
                input_device_index = self.audio.get_default_input_device_info()['index']
                
            # Store callback
            self.callback_fn = callback
                
            # Open stream with explicit settings
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            
            self.is_recording = True
            self.logger.info("Recording started successfully")
            
        except Exception as e:
            self.logger.error(f"Error in recording: {e}")
            if self.audio:
                self.audio.terminate()
            self.audio = None
            self.stream = None
            self.is_recording = False
            raise

        
    def stop(self):
        """Stop recording audio"""
        self.recording = False
        self.should_stop = True
        
        with self.stream_lock:
            if self.stream is not None:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    self.logger.info("Audio recording stopped")
                    
                    # Process the complete audio buffer
                    if self.frames:
                        self.logger.info(f"Processing {len(self.frames)} frames of audio...")
                        complete_audio = np.concatenate([np.frombuffer(f, dtype=np.float32) for f in self.frames])
                        
                        # Debug audio data
                        self.logger.info(f"Audio shape: {complete_audio.shape}")
                        self.logger.info(f"Audio max value: {np.max(np.abs(complete_audio))}")
                        self.logger.info(f"Audio min value: {np.min(complete_audio)}")
                        self.logger.info(f"Audio mean value: {np.mean(np.abs(complete_audio))}")
                        
                        if np.max(np.abs(complete_audio)) > 0:
                            self.logger.info("Sending audio to transcription")
                            if self.callback_fn:
                                self.callback_fn(complete_audio)
                        else:
                            self.logger.warning("No valid audio data detected")
                    
                except Exception as e:
                    self.logger.error(f"Error closing stream: {e}")