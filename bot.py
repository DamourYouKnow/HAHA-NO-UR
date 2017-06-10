import logging
from pathlib import Path
from time import time
from traceback import format_exc

from discord import Game
from discord.ext.commands import Bot, CommandNotFound, CommandOnCooldown
from websockets.exceptions import ConnectionClosed

from helpers import detailed_help, general_help_embed, get_command_collections
from logger import command_formatter, info, setup_logging


class HahaNoUR(Bot):
    def __init__(self, prefix: str):
        """
        Initialize an instance of the bot.

        :param prefix: the bot prefix
        """
        super().__init__(prefix)
        self.prefix = prefix
        self.log_path = Path(Path(__file__).parent.joinpath('logs'))
        self.start_time = int(time())
        self.logger = setup_logging(self.start_time, self.log_path)
        self.help_general = None
        self.help_detailed = {}

    async def on_ready(self):
        """
        Event for when the bot is ready.
        """
        print("Logged in")
        print(str(len(self.servers)) + " servers detected")

        async def __change_presence():
            try:
                await self.wait_until_ready()
                await self.change_presence(game=Game(name="combined args!"))
            except ConnectionClosed:
                await self.logout()
                await self.login()
                await __change_presence()

        await __change_presence()
        command_list, command_dict = get_command_collections(self)
        self.help_general = general_help_embed(self, command_dict)
        self.help_detailed = detailed_help(command_list)

    async def process_commands(self, message):
        """
        Overwrites the process_commands method to ignore bot users and
        log commands.
        """
        if message.author.bot:
            return
        await super().process_commands(message)
        content = message.content
        command_name = content.split(' ')[0][len(self.prefix):]
        if 'scout' in command_name.lower() and command_name in self.commands:
            log_entry = command_formatter(message, command_name)
            self.logger.log(logging.INFO, log_entry)
            info(log_entry, date=True)

    async def on_error(self, event_method, *args, **kwargs):
        """
        Runtime error handling
        """
        ig = 'Ignoring exception in {}\n'.format(event_method)
        tb = format_exc()
        self.logger.log(logging.CRITICAL, '\n' + ig + '\n' + tb)

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, CommandOnCooldown):
            await self._handle_command_error(exception, context)
        elif isinstance(exception, CommandNotFound):
            # Ignore this case
            return
        else:
            try:
                # Raise it again so we don't lose traceback
                raise exception
            except:
                tb = format_exc()
                triggered = context.message.content
                ex_type = type(exception).__name__
                four_space = ' ' * 4
                str_ex = str(exception)
                msg = '\n{0}Triggered message: {1}\n' \
                      '{0}Type: {2}\n' \
                      '{0}Exception: {3}\n{4}' \
                    .format(four_space, triggered, ex_type, str_ex, tb)
                self.logger.log(logging.WARNING, msg)

    async def _handle_command_error(self, exception, context):
        """
        Handle expected errors so no traceback is printed
        :param exception: the exception raised.
        :param context: the context of the exception.
        """
        if isinstance(exception, CommandOnCooldown):
            await self.send_message(context.message.channel, str(exception))
