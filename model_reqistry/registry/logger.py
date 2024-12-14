# from pathlib import Path
# from functools import wraps
# from datetime import datetime
import os
import logging
from .core.config import settings


def create_logger() -> logging.Logger:
    """
    Configure and return the model registry logger.

    Returns
    -------
    logging.Logger
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(settings.LOGGER_NAME)
    logger.setLevel(settings.LOG_LEVEL)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    file_handler = logging.FileHandler(f"./{settings.LOG_DIR}/{settings.LOGGER_NAME}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = create_logger()
