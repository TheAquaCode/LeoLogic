"""
Logging Utilities
"""

import logging
from pathlib import Path
from datetime import datetime


def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Setup a logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Optional log file path
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_processing(file_path: str, status: str, details: dict = None):
    """
    Log file processing events
    
    Args:
        file_path: Path to processed file
        status: Processing status (success, error, skipped)
        details: Additional details dictionary
    """
    logger = logging.getLogger("file_processor")
    
    message = f"File: {file_path} | Status: {status}"
    if details:
        message += f" | Details: {details}"
    
    if status == "error":
        logger.error(message)
    elif status == "success":
        logger.info(message)
    else:
        logger.warning(message)
