import os
import sys
import signal
from pathlib import Path
from echo.utils.logger import setup_logging
from echo.utils.notifications import NotificationManager
from echo.utils.config import load_config
from echo.voice_assistant import VoiceAssistant

def check_single_instance():
    """Ensure only one instance runs using a simple PID file"""
    pid_path = '/tmp/echo_assistant.pid'
    
    logger = setup_logging()
    logger.info(f"PID {os.getpid()} checking for existing instance")
    
    # Check for existing PID file
    if os.path.exists(pid_path):
        try:
            with open(pid_path, 'r') as f:
                old_pid = int(f.read().strip())
                # Check if process exists and is our app
                try:
                    import psutil
                    proc = psutil.Process(old_pid)
                    if proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE:
                        logger.info(f"Found running instance with PID {old_pid}")
                        return False
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    logger.info(f"Process {old_pid} not running, cleaning up")
                    os.unlink(pid_path)
        except (ValueError, FileNotFoundError):
            logger.info("Invalid PID file, cleaning up")
            try:
                os.unlink(pid_path)
            except FileNotFoundError:
                pass
    
    # Write our PID
    try:
        with open(pid_path, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"Created PID file with PID {os.getpid()}")
        return True
    except Exception as e:
        logger.error(f"Failed to create PID file: {e}")
        return False
        
def main():
    """Main entry point"""
    logger = setup_logging()
    logger.info(f"\n--- Starting Echo Assistant (PID: {os.getpid()}) ---")
    
    # Check for existing instance
    if not check_single_instance():
        logger.info("Another instance is already running")
        # Only show notification if we're the GUI instance
        if len(sys.argv) > 1 and sys.argv[1] == '--gui':
            try:
                notifications = NotificationManager()
                notifications.notify("Echo Assistant", "Already running!", "⚠️")
                logger.info("Sent 'already running' notification")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
        sys.exit(1)
            
    # Set up clean exit
    def cleanup(signum=None, frame=None):
        logger.info("Cleaning up...")
        try:
            os.unlink('/tmp/echo_assistant.pid')
            logger.info("Cleaned up PID file")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        os._exit(0)
    
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    
    try:
        logger.info("Initializing...")
        
        # Load configuration
        load_config()
        
        # Start voice assistant
        assistant = VoiceAssistant()
        assistant.run()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.exception("Fatal error in main loop")
        try:
            notifications = NotificationManager()
            notifications.notify(
                "Error",
                "Echo Assistant encountered an error and needs to be restarted.",
                "❌"
            )
        except Exception as notify_error:
            logger.error(f"Failed to send notification: {notify_error}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()