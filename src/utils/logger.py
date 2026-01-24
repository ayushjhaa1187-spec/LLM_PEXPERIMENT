"""
Logging Utility Module

This module provides a centralized logging configuration for the application,
including console and file handlers with rotation.

Author: LLM Government Consulting Team
Date: January 24, 2026
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from src.config import config


def setup_logger(name: str) -> logging.Logger:
    """Set up and return a logger with the specified name.
    
    Args:
        name: The name of the logger (usually __name__).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger
        
    logger.setLevel(config.logging.level)
    
    # Create formatters
    formatter = logging.Formatter(config.logging.format)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    try:
        log_file = Path(config.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            filename=config.logging.file_path,
            maxBytes=config.logging.max_bytes,
            backupCount=config.logging.backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
        
    return logger


# Default logger for main application
app_logger = setup_logger("app")
