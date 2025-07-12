import logging
import sys

FILENAME_LOG = 'yamdb'

_log_format = (
    '%(asctime)s - %(name)s - [%(levelname)s] - [%(color)s] - %(message)s - '
    '(%(filename)s -> %(funcName)s -> line %(lineno)d)'
)


class CustomFilter(logging.Filter):
    COLOR = {
        "DEBUG": "GREEN",
        "INFO": "GREEN",
        "WARNING": "YELLOW",
        "ERROR": "RED",
        "CRITICAL": "RED",
    }

    def filter(self, record):
        record.color = CustomFilter.COLOR[record.levelname]
        return True


def get_file_handler():
    file_handler = logging.FileHandler(f'{FILENAME_LOG}.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addFilter(CustomFilter())
    logger.addHandler(get_stream_handler())
    logger.addHandler(get_file_handler())
    return logger
