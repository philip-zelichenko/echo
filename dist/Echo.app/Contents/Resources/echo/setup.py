import os
import rumps
from pathlib import Path
from dotenv import load_dotenv, set_key

class SetupWindow(rumps.Window):
    def __init__(self):
        super().__init__(
            message="Please enter your OpenAI API key to get started:",
            title="Echo Setup",
            dimensions=(300, 100),
            ok="Save",
            cancel="Quit"
        )

def check_api_key():
    """Check if API key exists and is valid"""
    # Try to load from env first
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        # Show setup window
        window = SetupWindow()
        response = window.run()
        if response.clicked:
            api_key = response.text.strip()
            if api_key:
                # Save to .env file in user's config directory
                config_dir = Path.home() / '.echo'
                config_dir.mkdir(parents=True, exist_ok=True)
                env_path = config_dir / '.env'
                
                # Create or update .env file
                if not env_path.exists():
                    env_path.touch()
                set_key(str(env_path), 'OPENAI_API_KEY', api_key)
                
                # Reload environment after saving
                load_dotenv(env_path)
                
                # Verify the key was saved and loaded
                if os.getenv('OPENAI_API_KEY') == api_key:
                    return True
        return False
    return True