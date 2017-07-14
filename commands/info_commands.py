from time import time

from discord.ext import commands

from bot import HahaNoUR
from data import data_path


class Info:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot
        with data_path.joinpath('info.txt').open() as f:
            self.info_msg = f.read()

    @commands.command()
    async def info(self):
        """
        Description: Displays information about the bot.
        """
        await self.bot.say(self.info_msg)

    @commands.command()
    async def help(self, *, command=''):
        """
        Description: Help command.
        Usage: "`{prefix}help` for a list of all commands,
        `{prefix}help command name` for help for the specific command."
        """
        await self.bot.say(
            embed=self.bot.all_help.get(command, self.bot.help_general)
        )

    @commands.command()
    async def ping(self):
        """
        Description: Command to check network ping.
        Usage: "`{prefix}ping`"
        """
        start = time()
        msg = await self.bot.say('Loading... :hourglass:')
        end = time()
        diff = end - start
        await self.bot.edit_message(
            msg, new_content=f':ping_pong: Pong! | {round(diff*1000)}ms'
        )
