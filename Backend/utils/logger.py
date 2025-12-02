"""
Comprehensive Logging System with Colors and Rotation
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from config.settings import (
    LOGS_DIR, LOG_LEVEL, LOG_FORMAT, LOG_DATE_FORMAT,
    MAX_LOG_SIZE, BACKUP_COUNT
)


class ColoredFormatter(logging.Formatter):
    """Add colors to console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, log_file: str = None, level: str = None):
    """
    Setup a comprehensive logger with multiple handlers
    """
    logger = logging.getLogger(name)
    
    # Set default level if not already set
    if level:
        logger.setLevel(level)
    elif not logger.level:
        logger.setLevel(LOG_LEVEL)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    color_formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # 1. Console Handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG) # Allow all, let logger level control
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # 2. Main Rotating File Handler
    if log_file:
        file_path = LOGS_DIR / log_file
    else:
        file_path = LOGS_DIR / "leologic.log"
    
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG) # Allow all, let logger level control
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 3. Error-only Handler (separate file for errors)
    error_handler = RotatingFileHandler(
        LOGS_DIR / "errors.log",
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def update_log_level(level_name: str):
    """
    Dynamically update the log level for the root logger and all attached handlers.
    Maps UI labels (Verbose, Info) to Python logging constants.
    """
    level_map = {
        'Error': logging.ERROR,
        'Warning': logging.WARNING,
        'Info': logging.INFO,
        'Debug': logging.DEBUG,
        'Verbose': logging.DEBUG  # Python doesn't have Verbose, map to DEBUG
    }
    
    # Default to INFO if unknown
    new_level = level_map.get(level_name, logging.INFO)
    
    # Update root logger (affects all child loggers)
    logging.getLogger().setLevel(new_level)
    
    # Specifically update file_organizer loggers if they were instantiated separately
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(new_level)
        
    print(f"📝 Log level updated to: {logging.getLevelName(new_level)}")


def log_performance(func):
    """Decorator to log function execution time"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    
    return wrapper