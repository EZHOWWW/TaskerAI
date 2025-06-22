import logging
import sys


def setup_logging():
    """Configures the application's logger."""
    # Create a logger
    logger = logging.getLogger("task_processor")
    logger.setLevel(logging.INFO)

    # Create handlers
    # Console handler
    c_handler = logging.StreamHandler(sys.stdout)
    # File handler
    f_handler = logging.FileHandler("task_processor.log")

    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    c_handler.setFormatter(log_format)
    f_handler.setFormatter(log_format)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)

    return logger


logger = setup_logging()
