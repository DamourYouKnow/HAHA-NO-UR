import logging
from datetime import datetime
from pathlib import Path
from sys import stdout

from colorlog import ColoredFormatter
from discord import Message
from pytz import timezone

CONSOLE_FORMAT = '\n%(asctime)s:%(log_color)s%(levelname)s:%(name)s: ' \
                 '\033[0m%(message)s\n'
FILE_FORMAT = '\n%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'


def command_formatter(message: Message, command_name=None) -> str:
    """
    Format a command into a message to be logged.

    :param message: message object of requester
    :param command_name: optional identifier for request
    :return: the formatted log message
    """
    content = ''
    if command_name:
        content += command_name.title() + ' '

    content += 'from ' + message.author.name + '(' + message.author.id + ') '
    if message.server:
        content += 'in ' + message.server.name + ' #' + message.channel.name
    return content


def timestamp():
    """
    Gets the current timestamp

    :return: timestamp string with format yyyy-MM-dd hh:mm:ss AP/PM
    """
    return datetime.now(
        timezone('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p')


def setup_logging(start_time: int, path: Path):
    """
    Set up logging
    :param start_time: the start time of the log
    :param path: the path to the log folder
    :return: the logger object
    """
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    logger.addHandler(__get_file_handler(path, start_time))
    return logger


def __get_file_handler(path: Path, start_time: int):
    """
    Get a file handler for logging
    :param path: the log file path
    :param start_time: the start time
    :return: the file handler
    """
    handler = logging.FileHandler(
        filename=str(path.joinpath('{}.log'.format(start_time))),
        encoding='utf-8',
        mode='w+'
    )
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    return handler


def __get_console_handler():
    """
    Get a colourful console handler
    :return: the console handler
    """
    console = logging.StreamHandler(stdout)
    console.setFormatter(
        ColoredFormatter(
            CONSOLE_FORMAT,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'black,bg_blue',
                'INFO': 'black,bg_green',
                'WARNING': 'black,bg_yellow',
                'ERROR': 'black,bg_red',
                'CRITICAL': 'red,bg_white',
                'SILLY': 'black,bg_magenta'
            },
            secondary_log_colors={},
            style='%'
        )
    )
    console.setLevel(logging.INFO)
    return console


def warning(text, end=None, date=False):
    """
    Prints a yellow warning.
    """
    if date:
        text = "[" + timestamp() + "] | WARNING: " + text
    if end:
        print('\x1b[33m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[33m{}\x1b[0m'.format(text))


def error(text, end=None, date=False):
    """
    Prints a red error.
    """
    if date:
        text = "[" + timestamp() + "] | ERROR: " + text
    if end:
        print('\x1b[31m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[31m{}\x1b[0m'.format(text))


def info(text, end=None, date=False):
    """
    Prints a green info.
    """
    if date:
        text = "[" + timestamp() + "] | INFO: " + text
    if end:
        print('\x1b[32m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[32m{}\x1b[0m'.format(text))


def debug(text, end=None, date=False):
    """
    Prints a blue debug.
    """
    if date:
        text = "[" + timestamp() + "] | DEBUG: " + text
    if end:
        print('\x1b[34m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[34m{}\x1b[0m'.format(text))


def silly(text, end=None, date=False):
    """
    (lol)
    Prints a magenta/purple silly.
    """
    if date:
        text = "[" + timestamp() + "] | SILLY: " + text
    if end:
        print('\x1b[35m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[35m{}\x1b[0m'.format(text))
