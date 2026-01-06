import logging
from logging.handlers import RotatingFileHandler
import os

LOG_FILE_NAME = "trading_bot.log"
LOG_DIR = "logs"
MAX_BYTES = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5             # Keep up to 5 backup logs

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file_path = os.path.join(LOG_DIR, LOG_FILE_NAME)

def setup_logging():
    """
    Sets up a robust logging system for the trading bot.
    Logs to both console and a rotating file.
    """
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO) # Default logging level

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Prevent duplicate log messages if this function is called multiple times
    logger.propagate = False

    return logger

# Initialize logger when the module is imported
logger = setup_logging()

if __name__ == "__main__":
    # Test the logger
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    print(f"Log messages also written to {log_file_path}")
