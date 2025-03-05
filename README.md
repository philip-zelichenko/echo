# Echo - The Future of Hands-Free Communication
Echo is a next-generation voice assistant that transforms spoken words into natural, polished text messages. Powered by cutting-edge transcription technology and LLMs, Echo makes communication effortless—no keyboard required. Experience a future where typing is obsolete, and your voice does all the work. 🚀

## Features
- One-touch audio recording with F9 hotkey
- High-quality speech transcription using OpenAI's Whisper model
- Smart conversion of formal speech to casual text using GPT-3.5
- Seamless clipboard integration and automatic text input
- Cross-platform support (macOS, Linux)
- Configurable audio and AI settings
- Detailed logging system

## Prerequisites

- Python 3.8 or higher
- Poetry package manager
- OpenAI API key
- System requirements:
  - macOS: 10.15 or higher
  - Linux: PulseAudio or ALSA

## Setup

### 1. OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy your API key

### 2. Configure Environment
1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file:
   ```bash
   # Open with your preferred editor
   nano .env
   
   # Add your OpenAI API key
   OPENAI_API_KEY=sk-your-key-here
   ```

3. Update the service configuration:
   ```bash
   # Open the service configuration
   nano service/com.voiceassistant.plist
   
   # Update these values:
   <key>WorkingDirectory</key>
   <string>/Users/YOUR_USERNAME/path/to/echo</string>
   
   <key>OPENAI_API_KEY</key>
   <string>sk-your-key-here</string>
   ```

### 3. Verify Setup
1. Test the API key:
   ```bash
   # Stop the service if running
   ./scripts/manage.sh stop
   
   # Start in debug mode
   poetry run python -m echo.cli start
   ```

2. If successful, install as a service:
   ```bash
   ./scripts/install.sh
   ```

## Usage

1. Press F9 to start recording (default hotkey)
2. Speak your message naturally
3. Press F9 again to stop recording
4. Wait for processing (typically 1-2 seconds)
5. The casual version of your message will be automatically typed

### Example Transformations
Spoken: "I would like to inform you that I'll be arriving later than expected."
Result: "heads up, gonna be late!"

## Configuration

Configuration is managed in `src/echo/utils/config.py`. Key settings include:

### Audio Settings
- Sample rate (default: 44100Hz)
- Channels (default: 1)
- Recording device selection
- Audio format (WAV)

### Whisper Model Settings
- Model size (tiny, base, small, medium, large)
- Language detection
- Temperature and other inference parameters

### OpenAI API Settings
- API key configuration
- Model selection
- Temperature and token limits
- Retry settings

### Hotkey Configuration
- Customize recording trigger key
- Modifier key combinations

## Logging

Comprehensive logging system with:
- Real-time console output
- Rotating daily log files in `logs/` directory
- Debug level configuration
- Error tracking and reporting

## Project Structure

```bash
echo/
├── README.md
├── pyproject.toml          # Project dependencies and metadata
├── poetry.lock            # Locked dependencies
├── scripts/
│   ├── install.sh         # Installation script
│   └── uninstall.sh       # Uninstallation script
├── config/
│   └── com.voiceassistant.plist  # Service configuration
├── src/
│   └── echo/
│       ├── __init__.py
│       ├── transcriber.py         # Main transcription logic
│       ├── audio/
│       │   ├── __init__.py
│       │   └── recorder.py        # Audio recording handling
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration management
│       │   └── logger.py          # Logging setup
│       └── services/
│           ├── __init__.py
│           ├── transcription.py    # Whisper integration
│           └── openai_service.py   # GPT-3.5 integration
└── logs/
    └── .gitkeep
```

## Troubleshooting

Common issues and solutions:

1. **Recording not working**
   - Check microphone permissions
   - Verify audio input device in system settings
   - Ensure hotkey isn't conflicting with other applications

2. **Transcription errors**
   - Check internet connection
   - Verify OpenAI API key
   - Try adjusting microphone volume/position

3. **Service not starting**
   - Check installation logs
   - Verify system permissions
   - Ensure all dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and GPT-3.5
- The Python community for various dependencies
- Contributors and testers

## Support

For issues and feature requests, please use the GitHub issue tracker.
