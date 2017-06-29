from textwrap import wrap

from discord.ext.commands import CommandOnCooldown, Context

from bot.session_manager import HTTPStatusError


def command_error_handler(exception: Exception):
    """
    A function that handles command errors
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    ex_str = str(exception)
    if isinstance(exception, CommandOnCooldown):
        return ex_str
    if isinstance(exception, HTTPStatusError):
        msg = 'Something went wrong with the HTTP request.\n'
        return msg + ex_str
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
        '{four_space}Triggered message: {triggered}\n'
        '{four_space}Type: {ex_type}\n'
        '{four_space}Exception: {ex}'
    ).format(
        four_space=four_space,
        triggered=triggered,
        ex_type=ex_type, ex=str(ex)
    )

    return msg, triggered


def format_traceback(tb: str):
    """
    Format a traceback to be able to display in discord.
    :param tb: the traceback.
    :return: the traceback divided up into sections of max 1800 chars.
    """
    res = wrap(tb, 1800, replace_whitespace=False)
    str_out = ['```py\n' + s.replace('`', chr(0x1fef)) + '\n```'
               for s in res]
    return str_out
