import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Global flag to track if logger is initialized
_logger_initialized = False

def setup_logging():
    """Set up logging configuration"""
    global _logger_initialized
    
    # Only initialize once
    if _logger_initialized:
        return logging.getLogger('echo')
        
    # Create logs directory in user's home
    log_dir = Path.home() / '.echo_assistant' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Configure echo logger
    logger = logging.getLogger('echo')
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't propagate to root logger
    
    # File handler
    log_file = log_dir / 'echo_assistant.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Mark as initialized
    _logger_initialized = True
    
    return logger

def get_logger(name):
    """Get a logger instance"""
    if not _logger_initialized:
        setup_logging()
    return logging.getLogger(f'echo.{name}')