from textwrap import wrap

from discord.ext.commands import CommandOnCooldown, Context
from core.checks import NoMongo
from bot.session_manager import HTTPStatusError


def command_error_handler(exception: Exception):
    """
    A function that handles command errors
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    ex_str = str(exception)
    if isinstance(exception, (CommandOnCooldown, NoMongo)):
        return ex_str
    if isinstance(exception, HTTPStatusError):
        return f'Something went wrong with the HTTP request.\n{ex_str}'
    raise exception


def format_command_error(ex: Exception, context: Context) -> tuple:
    """
    Format a command error to display and log.
    :param ex: the exception raised.
    :param context: the context.
    :return: a message to be displayed and logged, and triggered message
    """
    triggered = context.message.content
    four_space = ' ' * 4
    ex_type = type(ex).__name__
    msg = (
        f'{four_space}Triggered message: {triggered}\n'
        f'{four_space}Type: {ex_type}\n'
        f'{four_space}Exception: {ex}'
    )

    return msg, triggered


def format_traceback(tb: str):
    """
    Format a traceback to be able to display in discord.
    :param tb: the traceback.
    :return: the traceback divided up into sections of max 1800 chars.
    """
    res = wrap(tb, 1800, replace_whitespace=False)
    return [f"```py\n{s.replace('`', chr(0x1fef))}\n```" for s in res]
