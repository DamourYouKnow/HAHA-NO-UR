import logging
from traceback import format_exc

from discord import Channel, Forbidden, Game, Object
from discord.ext.commands import Bot, CommandNotFound, Context
from websockets.exceptions import ConnectionClosed

from bot.error_handler import command_error_handler, format_command_error, \
    format_traceback
from bot.logger import command_formatter
from bot.session_manager import SessionManager
from core.help import get_help
from data_controller.mongo import MongoClient
from core import argument_parser


class HahaNoUR(Bot):
    def __init__(self, prefix: str, start_time: int, colour: int, logger,
                 session_manager: SessionManager, db: MongoClient,
                 error_log: int, feedback_log: int):
        """
        Init the instance of HahaNoUR.
        :param prefix: the bot prefix.
        :param start_time: the bot start time.
        :param colour: the colour used for embeds.
        :param logger: the logger.
        :param session_manager: the SessionManager instance.
        :param db: the MongoDB data controller.
        :param error_log: the channel id for error log.
        """
        super().__init__(prefix)
        self.prefix = prefix
        self.colour = colour
        self.start_time = start_time
        self.logger = logger
        self.help_general = None
        self.all_help = None
        self.db = db
        self.idol_names = []
        self.session_manager = session_manager
        # FIXME remove type casting after library rewrite
        self.error_log = Object(str(error_log))
        self.feedbag_log = Object(str(feedback_log))

    def start_bot(self, cogs: list, token: str):
        """
        Strat the bot.
        :param cogs: the list of cogs.
        :param token: the bot token.
        """
        for cog in cogs:
            self.add_cog(cog)
        self.run(token)

    async def __change_presence(self):
        """
        Change the "Playinng" status of the bot.
        """
        try:
            await self.wait_until_ready()
            await self.change_presence(game=Game(name='!scouts'))

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
        self.help_general, self.all_help = get_help(self)
        self.idol_names = await self.db.cards.get_idol_names()
        await self.__change_presence()

    async def process_commands(self, message):
        """
        Overwrites the process_commands method to ignore bot users and
        log commands.
        """
        if message.author.bot or len(message.content) < 1:
            return
        
        content = message.content
    
        # Look up any custom prefixes and replace them with the bot prefix.
        if message.server:
            custom_prefix = await self.db.servers.get_prefix(message.server.id)
            if content.startswith(custom_prefix):
                content = self.prefix + content[len(custom_prefix):]
            elif content.startswith(self.prefix) and self.prefix != custom_prefix:
                content = content[1:]

        # Pull alarm in case of emergency.
        if content.split(' ')[0].startswith('resetprefix'):
            content = self.prefix + 'resetprefix'

        is_cmd = (content[0] == self.prefix)
        command_name = content.split(' ')[0][len(self.prefix):]
        if is_cmd and command_name in list(self.commands.keys()):
            log_entry = command_formatter(message, self.prefix + command_name)
            self.logger.log(logging.INFO, log_entry)
            
        message.content = content
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
            try:
                await self.send_message(channel, base)
            except Forbidden:
                pass
        finally:
            self.logger.log(lvl, log_msg)
            await self.send_traceback(tb, header)

    async def __try_send_msg(self, channel, author, msg):
        try:
            await self.send_message(channel, msg)
        except Forbidden:
            pass

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, Forbidden):
            # Ignore this case
            return
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

            await self.__try_send_msg(channel, context.message.author, warn)
            await self.send_traceback(
                tb, f'**WARNING** Triggered message:\n{triggered}')
        else:
            await self.__try_send_msg(channel, context.message.author, res)
