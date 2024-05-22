import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(logger_name):
    """
    Function to configure the logger with basic formatting and file rotation.
    """
    logger = logging.getLogger(logger_name)

    if not logger.hasHandlers():  # Ensure no duplicate handlers
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')

        log_file_path = f'./logs/daily_report_{datetime.now().strftime("%d%m%y")}.log'
        directory = os.path.dirname(log_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # File handler with rotation
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=3)  # 5 MB files, keep 3 backups
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def log_info(logger, message):
    """Logs an info message."""
    logger.info(str(message).strip())

def log_debug(logger, message):
    """Logs a debug message."""
    logger.debug(str(message).strip())

def log_error(logger, message):
    """Logs an error message."""
    logger.error(str(message).strip())

def log_success(logger, message):
    """Logs a success message."""
    logger.info(f"[SUCCESS] {message}")

def log_failed(logger, message):
    """Logs a failed message."""
    logger.error(f"[FAILED] {message}")

def log_warning(logger, message):
    """Logs a warning message."""
    logger.warning(f"[WARNING] {message}")
