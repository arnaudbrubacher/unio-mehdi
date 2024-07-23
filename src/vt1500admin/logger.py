from datetime import datetime
import logging
import os

def setup_logger(path, name, log_level=logging.DEBUG):

    time_tag = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


    log_path = os.path.join(path, name + "-" + time_tag + '.log')

    logger = logging.getLogger("LOGGER")
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_path, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    logger.info("Logger started...")

def info(text):
    logger = logging.getLogger("LOGGER")
    if text[:7] != "[EVENT]":
        logger.info(text)


def debug(text):
    logger = logging.getLogger("LOGGER")
    if text[:7] != "[EVENT]":
        logger.debug(text)

def error(ex):
    logger = logging.getLogger("LOGGER")
    logger.error(str(ex))
