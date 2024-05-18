import logging
import os
from datetime import datetime

def setup_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.setLevel(logging.DEBUG)


    formatter = logging.Formatter('[%(asctime)s]  [%(levelname)s]  [%(name)s]  %(message)s')

    
    log_file_path = f'./logs/daily_report_{datetime.now().strftime("%d%m%y")}.log'
    directory = os.path.dirname(log_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger

def log_info(logger, message):
    logger.info(str(message).strip())

def log_debug(logger, message):
    logger.debug(str(message).strip())

def log_error(logger, message):
    logger.error(str(message).strip())
