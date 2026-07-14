import logging
import os

def log_config(timestamp:str,log_dir:str):
    """
    Sets up logging configuration for the application.

    Args:
        timestamp (str): For the filename of the logs.
        log_dir (str): Where we want the logs stored.

    Returns:
        logger (logging.Logger): Configured logger instance.
    """

    os.makedirs(log_dir, exist_ok=True)
    log_filename = f'{log_dir}/{timestamp}.log'

    handlers=[
        logging.FileHandler(f"{log_filename}"),  # Saves to file
        logging.StreamHandler()                        # Prints to terminal
    ]
    logging.basicConfig(
        format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        force=True,
        handlers=handlers
    )

    logger = logging.getLogger()
    return logger