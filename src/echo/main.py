import os
import sys
import time
import signal
import subprocess
import threading  # Add this import
from pathlib import Path

from echo.utils.logger import setup_logging
from echo.utils.input_handler import InputHandler
from echo.utils.permissions import PermissionsManager

from echo.utils.notifications import NotificationManager
from echo.utils.config import load_config
from echo.setup import check_api_key
from echo.voice_assistant import VoiceAssistant


def check_single_instance():
    """Ensure only one instance runs using a simple PID file"""
    pid_path = '/tmp/echo_assistant.pid'
    
    logger = setup_logging()
    logger.info(f"PID {os.getpid()} checking for existing instance")
    
    try:
        # Check if PID file exists
        if os.path.exists(pid_path):
            with open(pid_path, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Check if process is actually running
            try:
                os.kill(old_pid, 0)  # Test if process exists
                logger.info(f"Found running instance with PID {old_pid}")
                return False
            except OSError:  # Process not found
                logger.info(f"Removing stale PID file for {old_pid}")
                os.unlink(pid_path)
        
        # Write our PID
        with open(pid_path, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"Created PID file with PID {os.getpid()}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to check/create PID file: {e}")
        return False
            
def main():
    """Main entry point"""
    logger = setup_logging()
    logger.info(f"\n--- Starting Echo (PID: {os.getpid()}) ---")
    
    if not check_single_instance():
        logger.info("Another instance is already running")
        sys.exit(0)
    
    # Check all permissions before starting
    permissions = PermissionsManager()
    
    # Only check permissions once at startup
    if not permissions.check_all_permissions():
        logger.error("Missing required permissions")
        sys.exit(0)  # Exit cleanly
    
    try:
        # Initialize GUI
        from echo.gui import EchoGUI
        app = EchoGUI()
        
        # Initialize voice assistant
        assistant = VoiceAssistant()
        
        # Connect GUI and assistant
        app.set_voice_assistant(assistant)
        
        # Start keyboard listener
        if not assistant.start_keyboard_listener():
            logger.error("Failed to initialize keyboard listener")
            
        # Start assistant thread
        assistant_thread = threading.Thread(target=assistant.run, daemon=True)
        assistant_thread.start()
        
        # Check for API key
        if not check_api_key():
            logger.error("No API key provided - exiting")
            sys.exit(1)
        
        # Run GUI main loop
        app.run()
                    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
                        
if __name__ == "__main__":
    main()