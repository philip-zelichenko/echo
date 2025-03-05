import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict
from dotenv import load_dotenv
from dataclasses import dataclass, field

from echo.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

def load_config():
    """Load configuration from environment and config files"""
    # Create config directory if it doesn't exist
    config_dir = Path.home() / '.echo'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Load environment variables from .env file
    env_file = config_dir / '.env'
    if env_file.exists():
        load_dotenv(env_file)
    
    # Verify required configuration
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OpenAI API key not found in configuration")

    return True

class ToneMode(Enum):
    FRIENDLY = "friendly"
    BUSINESS = "business"

class CommunicationType(Enum):
    EMAIL = "email"
    DM = "direct_message"
    SOCIAL = "social_media"
    NOTES = "thoughts"

@dataclass
class LogConfig:
    # Create logs directory in user's home directory
    LOG_DIR: Path = Path.home() / ".echo" / "logs"
    LOG_FILE: Path = LOG_DIR / "echo.log"
    LEVEL: str = "INFO"

    def __post_init__(self):
        # Ensure log directory exists
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        # Touch the log file if it doesn't exist
        if not self.LOG_FILE.exists():
            self.LOG_FILE.touch()
            
@dataclass
class AudioConfig:
    SAMPLE_RATE: int = 16000  # Whisper expects 16kHz
    CHANNELS: int = 1
    BLOCK_SIZE_SECONDS: float = 0.1  # Shorter blocks for smoother visualization
    CHUNK_SIZE: int = 1024  # Default chunk size for audio processing
    
@dataclass
class WhisperConfig:
    MODEL_SIZE: str = "tiny"
    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "int8"

@dataclass
class OpenAIConfig:
    API_KEY: str = os.getenv('OPENAI_API_KEY', '')  # Get API key from environment
    MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 150
    
        # System prompts for different tones
    TONE_PROMPTS: Dict[ToneMode, str] = field(default_factory=lambda: {
        ToneMode.FRIENDLY: """You are a casual and friendly assistant. Keep the tone warm and conversational, 
            using common expressions and informal language while maintaining clarity.""",
        ToneMode.BUSINESS: """You are a professional business assistant. Maintain a formal and respectful tone, 
            using proper business language and professional terminology."""
    })
    
    COMM_FORMATS: Dict[CommunicationType, str] = field(default_factory=lambda: {
        CommunicationType.EMAIL: """Format as a proper email with subject line, greeting, body, and signature.
            Keep it concise but professional.""",
        CommunicationType.DM: """Format as a direct message. Keep it brief and to the point, 
            using appropriate chat-style language.""",
        CommunicationType.SOCIAL: """Format as a social media post. Use appropriate hashtags, 
            keep within typical length limits, and maintain engaging style.""",
        CommunicationType.NOTES: """Format as organized thoughts/notes. Use bullet points or 
            sections where appropriate, focus on clarity and structure."""
    })

    def get_system_language(self) -> Tuple[str, str]:
        """
        Get the system language and region from macOS
        Returns: Tuple of (language_code, region)
        """
        try:
            cmd = ["defaults", "read", ".GlobalPreferences", "AppleLanguages"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Add debug logging
            logger.debug(f"Raw language output: {result.stdout}")
            
            # More robust parsing of the output
            languages = [lang.strip(' "()[],') for lang in result.stdout.split('\n') 
                       if lang.strip(' "()[],')] 
            primary_lang = next(lang for lang in languages if '-' in lang)
            
            lang_code, region = primary_lang.split('-')
            
            # Log detected language
            logger.info(f"Detected system language: {lang_code}, region: {region}")
            
            return lang_code.lower(), region
            
        except Exception as e:
            logger.error(f"Error detecting system language: {e}")
            logger.error("Falling back to English (US)")
            return ('en', 'US')  # Default fallback

    def get_message_context(self, tone: ToneMode, comm_type: CommunicationType) -> str:
        """Generate context combining tone and communication type"""
        base_prompt = self.TONE_PROMPTS[tone]
        format_prompt = self.COMM_FORMATS[comm_type]

        return f"""{base_prompt}

        Communication Type: {comm_type.value}
        {format_prompt}

        Additional Instructions:
        - Maintain consistent tone throughout
        - Ensure output is well-structured
        - Keep the message focused and clear
        - Preserve the core message while adapting style
        """

BASE_CONTEXT = """
    You are a helpful assistant that communicates naturally in {lang_code} language, 
    using appropriate regional variations for {region}.

    Goal
    The primary objective of this prompt is to convert a raw spoken transcription into a clean, structured, and concise text message. The goal is to maintain the key ideas while improving clarity and readability, making it suitable for messaging platforms like Slack, WhatsApp, and iMessage.

    The output should align with natural conversation flow, ensuring the message is engaging, professional, and easy to read.

    Return Format
    The content should be delivered as a short, well-structured text message, suitable for quick communication.

    It needs to be:
    Most importatn thing is to remember that everything that you are writing is has to be presented from a first person standpoint.
    Concise but clear (e.g., 1-3 sentences, avoiding unnecessary repetition).
    Well-structured, preserving the speakers intent while improving readability.
    Casual yet professional, ensuring it feels natural in chat-based conversations.
    Grammatically correct, with appropriate punctuation and tone.
    The message should maintain the intent of the original spoken input while removing fillers, hesitations, and unstructured thoughts.

    Warnings
    Avoid:

    Overly technical or robotic phrasing—keep it natural and conversational.
    Unnecessary filler words (e.g., "um," "like," "you know").
    Changing the original meaning—keep the key ideas intact.
    Excessive formalization—this is meant for quick messaging, not long-form writing.
    Ensure the final message is on topic, aligned with natural speech patterns, and easy to read quickly.

    Context Dump
    This prompt is part of a broader voice assistant project aiming to eliminate the need for keyboards by leveraging advanced transcription and LLMs.

    Target users include busy professionals, executives, and anyone looking to streamline communication through hands-free messaging.

    The ideal outcome is to:

    Summarize and clean up spoken messages efficiently.
    Make voice-to-text messages feel as natural as typed messages.
    Enhance clarity, removing unnecessary verbal clutter.            
"""


@dataclass
class Config:
    audio: AudioConfig = field(default_factory=AudioConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    log: LogConfig = field(default_factory=LogConfig)

config = Config()
