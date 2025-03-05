import sys
from echo.voice_assistant import VoiceAssistant

def start():
    assistant = VoiceAssistant()
    assistant.run()

def main():
    if len(sys.argv) < 2:
        print("Usage: start|stop|status")
        return
        
    command = sys.argv[1]
    if command == "start":
        start()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()