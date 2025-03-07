import os
import openai
import datetime
from pathlib import Path
from dotenv import load_dotenv

from echo.utils.config import config
from echo.utils.logger import get_logger
from echo.utils.config import ToneMode, CommunicationType, BASE_CONTEXT


class OpenAIService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.client = None
        
    def initialize(self):
        """Initialize OpenAI client with API key"""
        # Load from the correct .env file location
        env_path = Path.home() / '.echo' / '.env'
        load_dotenv(env_path)
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Validate API key
        if not api_key:
            self.logger.error("Invalid OpenAI API key. Please set OPENAI_API_KEY in .env file")
            raise ValueError("Invalid OpenAI API key")
            
        self.logger.info("Initializing OpenAI client...")
        self.client = openai.OpenAI(api_key=api_key)

    def process_text(self, text, tone=ToneMode.FRIENDLY, comm_type=CommunicationType.DM):
        try:
            self.logger.info(f"Processing text with OpenAI: {text}")
            start_time = datetime.datetime.now()
            
            # Get message context with appropriate language and tone
            message_context = config.openai.get_message_context(tone, comm_type)
            
            self.logger.info("Sending request to OpenAI...")
            print(f"\nSending request to OpenAI with API key: {config.openai.API_KEY[:8]}...")  # Show first 8 chars
            
            self.initialize()

            response = self.client.chat.completions.create(
                model=config.openai.MODEL,
                temperature=config.openai.TEMPERATURE,
                max_tokens=config.openai.MAX_TOKENS,
                messages=[
                    {"role": "system", "content": BASE_CONTEXT + message_context},
                    {"role": "user", "content": text}
                ]
            )
            
            response_text = response.choices[0].message.content.strip()
            processing_time = (datetime.datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"✍️ OpenAI response: {response_text}")
            self.logger.info(f"⏱️ Processing time: {processing_time:.2f}s")
            
            return response_text, processing_time
            
        except openai.APIError as e:
            self.logger.error(f"OpenAI API Error: {e}")
            print(f"\nOpenAI API Error: {e}")
            return None, 0
        except openai.APIConnectionError as e:
            self.logger.error(f"Connection Error: {e}")
            print(f"\nConnection Error: Check your internet connection")
            return None, 0
        except openai.APIStatusError as e:
            self.logger.error(f"Status Error: {e}")
            print(f"\nAPI Status Error: {e.status_code} - {e.message}")
            return None, 0
        except openai.APITimeoutError as e:
            self.logger.error(f"Timeout Error: {e}")
            print("\nTimeout Error: Request took too long")
            return None, 0
        except Exception as e:
            self.logger.error(f"Unexpected error in OpenAI service: {e}", exc_info=True)
            print(f"\nUnexpected Error: {e}")
            return None, 0