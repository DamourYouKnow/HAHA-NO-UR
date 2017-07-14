import logging
from traceback import format_exc

from discord import Channel, Game, Object
from discord.ext.commands import Bot, CommandNotFound, Context
from websockets.exceptions import ConnectionClosed

from bot.error_handler import command_error_handler, format_command_error, \
    format_traceback
from bot.logger import command_formatter
from bot.session_manager import SessionManager
from core.helpers import detailed_help, general_help_embed, \
    get_command_collections, get_valid_commands
from data_controller.mongo import DatabaseController


class HahaNoUR(Bot):
    def __init__(self, prefix: str, start_time: int, logger,
                 session_manager: SessionManager, db: DatabaseController,
                 error_log: int):
        """
        Initialize an instance of the bot.
        :param session_manager: the session manager used for HTTP requests.
        :param prefix: the bot prefix.
        :param start_time: the start time.
        :param logger: the logger.
        :param error_log: the error log channel id.
        """
        super().__init__(prefix)
        self.prefix = prefix
        self.start_time = start_time
        self.logger = logger
        self.help_general = None
        self.help_detailed = {}
        self.db = db
        self.all_commands = []
        self.session_manager = session_manager
        # FIXME remove type casting after library rewrite
        self.error_log = Object(str(error_log))

    def start_bot(self, cogs: list, token: str):
        """
        Strat the bot.
        :param cogs: the list of cogs.
        :param token: the bot token.
        """
        for cog in cogs:
            self.add_cog(cog)
        command_list, command_dict = get_command_collections(self)
        self.help_general = general_help_embed(self, command_dict)
        self.help_detailed = detailed_help(command_list, self.logger)
        self.all_commands = get_valid_commands(self)
        self.run(token)

    async def __change_presence(self):
        """
        Change the "Playinng" status of the bot.
        """
        try:
            await self.wait_until_ready()
            await self.change_presence(game=Game(name='!album'))
        except ConnectionClosed:
            await self.logout()
            await self.login()
            await self.__change_presence()

    async def send_traceback(self, tb, header):
        """
        Send traceback to the error log channel.
        :param tb: the traceback.
        :param header: the header for the error.
        """
        await self.send_message(self.error_log, header)
        for s in format_traceback(tb):
            await self.send_message(self.error_log, s)

    async def on_ready(self):
        """
        Event for when the bot is ready.
        """
        self.logger.log(logging.INFO, 'Logged in')
        self.logger.log(logging.INFO, f'{len(self.servers)} servers detected')
        await self.__change_presence()

    async def process_commands(self, message):
        """
        Overwrites the process_commands method to ignore bot users and
        log commands.
        """
        if message.author.bot:
            return

        content = message.content
        command_name = content.split(' ')[0][len(self.prefix):]
        if command_name in self.all_commands:
            log_entry = command_formatter(message, self.prefix + command_name)
            self.logger.log(logging.INFO, log_entry)

        await super().process_commands(message)

    async def on_error(self, event_method, *args, **kwargs):
        """
        Runtime error handling
        """
        ig = f'Ignoring exception in {event_method}\n'
        tb = format_exc()
        log_msg = f'\n{ig}\n{tb}'
        header = f'**CRITICAL**\n{ig}'
        lvl = logging.CRITICAL
        base = (':x: I ran into a critical error, '
                'it has been reported to my developers.')
        try:
            ctx = args[1]
            channel = ctx.message.channel
            assert isinstance(ctx, Context)
            assert isinstance(channel, Channel)
        except (IndexError, AssertionError, AttributeError):
            pass
        else:
            header = f'**ERROR**\n{ig}'
            lvl = logging.ERROR
            await self.send_message(channel, base)
        finally:
            self.logger.log(lvl, log_msg)
            await self.send_traceback(tb, header)

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, CommandNotFound):
            # Ignore this case
            return
        channel = context.message.channel
        try:
            res = command_error_handler(exception)
        except Exception as e:
            tb = format_exc()
            msg, triggered = format_command_error(e, context)
            self.logger.log(logging.WARN, f'\n{msg}\n\n{tb}')
            warn = (f':warning: I ran into an error while executing this '
                    f'command. It has been reported to my developers.\n{msg}')
            await self.send_message(channel, warn)
            await self.send_traceback(
                tb, f'**WARNING** Triggered message:\n{triggered}')
        else:
            await self.send_message(channel, res)
