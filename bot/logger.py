import logging
from datetime import datetime
from pathlib import Path
from sys import stdout

from colorlog import ColoredFormatter
from discord import Message
from pytz import timezone

CONSOLE_FORMAT = ('%(asctime)s %(log_color)s%(levelname)s %(name)s: '
                  '%(message)s')
FILE_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


def command_formatter(message: Message, command_name=None) -> str:
    """
    Format a command into a message to be logged.

    :param message: message object of requester
    :param command_name: optional identifier for request
    :return: the formatted log message.
    """
    command = command_name or ''
    server = f'in {message.server} #{message.channel}' \
        if message.server else None
    return f'{command} from {message.author} ({message.author.id}) {server}'


def timestamp(*args):
    """
    Gets the current timestamp

    :return: timestamp string with format yyyy-MM-dd hh:mm:ss AP/PM
    """
    return datetime.now(timezone('Canada/Eastern')).timetuple()


def setup_logging(start_time, path: Path):
    """
    Set up logging
    :param start_time: the start time of the log
    :param path: the path to the log folder
    :return: the logger object
    """
    logging.Formatter.converter = timestamp
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler(path, start_time))
    logger.addHandler(get_console_handler())
    return logger


def get_file_handler(path: Path, start_time):
    """
    Get a file handler for logging
    :param path: the log file path
    :param start_time: the start time
    :return: the file handler
    """
    handler = logging.FileHandler(
        filename=path.joinpath(f'{int(start_time)}.log'),
        encoding='utf-8',
        mode='w+'
    )
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    return handler


def get_console_handler():
    """
    Get a colourful console handler
    :return: the console handler
    """
    console = logging.StreamHandler(stdout)
    console.setFormatter(
        ColoredFormatter(
            CONSOLE_FORMAT,
            datefmt='%y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
    )
    return console
