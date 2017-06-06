from datetime import datetime

from discord import Message
from pytz import timezone

FILENAME = 'log.txt'


def log_message(content: str):
    """
    Writes a message to the log file

    :param content: message being logged
    """
    with open(FILENAME, 'a') as fp:
        fp.write(_timestamp() + ' | ' + content + '\n')
        fp.close()


def log_request(message: Message, request_name=None):
    """
    Writes a request to a log file

    :param message: message object of requester
    :param request_name: optional identifier for request
    """
    content = ''
    if request_name is not None:
        content += request_name.title() + ' '

    content += 'from ' + message.author.name + '(' + message.author.id + ') '
    content += 'in ' + message.server.name + ' #' + message.channel.name

    log_message(content)


def _timestamp():
    """
    Gets the current timestamp

    :return: timestamp string with format yyyy-MM-dd hh:mm:ss AP/PM
    """
    time = datetime.now(timezone('US/Eastern'))
    return time.strftime('%Y-%m-%d %I:%M:%S %p')
