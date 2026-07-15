import logging
import os
import sys

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

    # INFO/DEBUG to stdout
    stdout_stream_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_stream_handler.setLevel(logging.DEBUG)
    stdout_file_handler = logging.FileHandler(f"{log_filename}")
    stdout_file_handler.setLevel(logging.DEBUG)
    stdout_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdout_stream_handler.setFormatter(stdout_fmt)

    # WARN/ERROR to stderr
    stderr_stream_handler = logging.StreamHandler(stream=sys.stderr)
    stderr_stream_handler.setLevel(logging.WARNING)
    stderr_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stderr_stream_handler.setFormatter(stderr_fmt)


    logger.handlers = []          # clear defaults
    logger.addHandler(stdout_stream_handler)
    logger.addHandler(stderr_stream_handler)

    # logging.basicConfig(
    #     format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     level=logging.INFO,
    #     force=True,
    #     handlers=handlers
    # )

    logger = logging.getLogger()
    return logger
  