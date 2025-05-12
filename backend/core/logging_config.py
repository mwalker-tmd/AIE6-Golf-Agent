import logging
from typing import Optional

# Create a custom logger
logger = logging.getLogger("golf_agent")
logger.setLevel(logging.INFO)  # Default level

# Create console handler with formatting
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def set_log_level(level: str) -> None:
    """
    Set the logging level for the application.
    
    Args:
        level: One of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    """
    level = level.upper()
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    
    if level not in valid_levels:
        raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
    
    logger.setLevel(getattr(logging, level))
    logger.info(f"Log level set to {level}")

def get_log_level() -> str:
    """
    Get the current logging level.
    
    Returns:
        str: Current logging level name
    """
    return logging.getLevelName(logger.level) 