from discord.ext import commands

from bot import HahaNoUR
from data import data_path


class InfoCommands:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot
        with data_path.joinpath('info.txt').open() as f:
            self.info_msg = f.read()

    @commands.command()
    async def info(self):
        """
        Display a info message.
        """
        await self.bot.say(self.info_msg)

    @commands.command()
    async def help(self, command=None):
        """
        Display this message.
        """
        if command is None:
            await self.bot.say(embed=self.bot.help_general)
            return
        for key, val in self.bot.help_detailed.items():
            if command in key:
                await self.bot.say(embed=val)
                return
        await self.bot.say(embed=self.bot.help_general)
