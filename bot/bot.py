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
from data_controller.mongo import DatabaseController


class HahaNoUR(Bot):
    def __init__(self, prefix: str, start_time: int, colour: int, logger,
                 session_manager: SessionManager, db: DatabaseController,
                 error_log: int):
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
        self.run(token)

    def get_command_collections(self) -> tuple:
        """
        Return a list and a dict of the bot commands.
        :param bot: the bot.
        :return: A tuple of (list of bot commands, dict of bot commands)
        The list contains tuples of (tuple of command name, command help)
        The dict has cog name as key and list of tuple of name as val
        """
        aliases = []
        command_list = []
        command_dict = {}
        for key, val in self.commands.items():
            cog_name = val.cog_name
            command_help = val.help
            name = None
            if key.startswith('_'):
                aliases += val.aliases
                name = tuple([n for n in val.aliases if not n.startswith('_')])
            elif str(val) not in aliases and not str(val).startswith('_'):
                name = (str(val),)
            if name:
                command_list.append((name, command_help))
                if cog_name not in command_dict:
                    command_dict[cog_name] = []
                command_dict[cog_name].append(name)
        return command_list, command_dict

    def get_valid_commands(self):
        """
        Return a list of every valid user command, including aliases.

        :return: Command list.
        """
        cmds = []
        for cmd_and_aliases in self.get_command_collections()[1].values():
            for alias_tuple in cmd_and_aliases:
                for alias in alias_tuple:
                    cmds.append(alias)
        return cmds

    async def __change_presence(self):
        """
        Change the "Playinng" status of the bot.
        """
        try:
            await self.wait_until_ready()
            await self.change_presence(game=Game(name='!info'))
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
        self.all_commands = self.get_valid_commands()
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
        print(command_name)
        print(self.all_commands)
        if command_name in self.all_commands:
            print("hello")
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
            msg = ("It appears I don't have permission to post messages and "
                   "send files. Please make sure I can do this!")
            await self.send_message(author, msg)

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

            await self.__try_send_msg(channel, context.message.author, warn)
            await self.send_traceback(
                tb, f'**WARNING** Triggered message:\n{triggered}')
        else:
            await self.__try_send_msg(channel, context.message.author, res)
