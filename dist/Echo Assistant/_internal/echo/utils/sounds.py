import simpleaudio as sa
import numpy as np
from echo.utils.logger import get_logger

def generate_beep(frequency, duration, volume=0.3):
    """Generate a beep sound"""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    samples = np.sin(2 * np.pi * frequency * t)
    audio = (volume * samples * 32767).astype(np.int16)
    return audio

def play_start_sound():
    """Play start recording sound"""
    try:
        audio = generate_beep(1000, 0.1)  # High pitch beep
        play_obj = sa.play_buffer(audio, 1, 2, 44100)
        play_obj.wait_done()
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error playing start sound: {e}")

def play_stop_sound():
    """Play stop recording sound"""
    try:
        audio = generate_beep(500, 0.1)  # Low pitch beep
        play_obj = sa.play_buffer(audio, 1, 2, 44100)
        play_obj.wait_done()
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Error playing stop sound: {e}")