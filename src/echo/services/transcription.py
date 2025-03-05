import numpy as np
from faster_whisper import WhisperModel
from echo.utils.config import config
from echo.utils.logger import get_logger

class Transcriber:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("Initializing Transcriber...")
        
        # Load model with explicit model size
        try:
            self.model = WhisperModel(
                model_size_or_path="base",  # Use "base" model
                device="cpu",
                compute_type="int8"
            )
            self.logger.info("Whisper model loaded successfully")
            
            # Set parameters
            self.beam_size = 5
            self.best_of = 5
            self.temperature = 0.0
            self.compression_ratio_threshold = 2.4
            self.condition_on_previous_text = True
            
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {e}")
            raise

    def transcribe_audio(self, audio):
        try:
            self.logger.info(f"Starting transcription. Audio shape: {audio.shape}")
            
            # Convert stereo to mono if needed
            if len(audio.shape) > 1 and audio.shape[1] > 1:
                audio = np.mean(audio, axis=1)
            
            # Ensure audio is 1D array
            audio = audio.flatten()
            
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
                self.logger.info("Audio normalized successfully")
            else:
                self.logger.warning("Audio is empty or silent")
                return ""

            # Transcribe with improved parameters
            self.logger.info("Calling Whisper model...")
            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=self.beam_size,
                best_of=self.best_of,
                temperature=self.temperature,
                compression_ratio_threshold=self.compression_ratio_threshold,
                condition_on_previous_text=self.condition_on_previous_text,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=300,
                    speech_pad_ms=300,
                    threshold=0.3
                )
            )
            self.logger.info("Whisper transcription completed")
            
            # Get text from segments
            segments_list = list(segments)
            self.logger.info(f"Number of segments: {len(segments_list)}")
            
            if not segments_list:
                self.logger.warning("No segments returned from Whisper")
                return ""
                
            text = " ".join([segment.text for segment in segments_list])
            self.logger.info(f"Final transcribed text: {text}")
            print(f"\nTranscribed text: {text}")
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error in transcription: {e}", exc_info=True)
            print(f"\nTranscription error: {e}")
            return ""