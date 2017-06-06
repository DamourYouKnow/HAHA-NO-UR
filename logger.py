from datetime import datetime

from discord import Message
from pytz import timezone

FILENAME = 'log.txt'


def log_message(content: str):
    """
    Writes a message to the log file

    content: String - message being logged
    """
    with open(FILENAME, 'a') as fp:
        fp.write(timestamp() + ' | ' + content + '\n')


def log_request(message: Message, request_name=None):
    """
    Writes a request to a log file

    :param message: message object of requester
    :param request_name:
    """
    content = ''
    if request_name is not None:
        content += request_name.title() + ' '

    content += 'from ' + message.author.name + '(' + message.author.id + ') '
    content += 'in ' + message.server.name + ' #' + message.channel.name

    log_message(content)


def timestamp():
    """
    Gets the current timestamp

    return: String - timestamp
    """
    time = datetime.now(timezone('US/Eastern'))
    return time.strftime('%Y-%m-%d %I:%M:%S %p')
