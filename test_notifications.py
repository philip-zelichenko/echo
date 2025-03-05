import sys

# Force immediate output
sys.stdout.flush()

print("Starting test...", flush=True)

try:
    print("Importing modules...", flush=True)
    from echo.utils.notifications import NotificationManager
    from echo.utils.logger import setup_logging
    
    print("Setting up logging...", flush=True)
    logger = setup_logging()
    
    print("Creating notification manager...", flush=True)
    notifications = NotificationManager()
    
    print("Sending test notification...", flush=True)
    notifications.notify(
        "Test Title",
        "Test Message",
        "🔔"
    )
    print("Notification sent!", flush=True)
    
except Exception as e:
    print(f"Error occurred: {e}", flush=True)
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}", flush=True)

print("Test complete!", flush=True)