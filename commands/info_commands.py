from time import time

from discord.ext import commands

from bot import HahaNoUR


class InfoCommands:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command()
    async def info(self):
        # TODO D'Amour read this from file.
        reply = ("**2017-06-18:** Albums have been added!\n\n"
                 "Instructions for how to use the bot can be found here:\n"
                 "<https://github.com/DamourYouKnow/"
                 "HAHA-NO-UR/blob/master/README.md>\n\n"
                 "If you have any suggestions for new feautures or "
                 "improvements contact D'Amour#2601 on discord or submit "
                 "a request on our dev channel or on github:\n"
                 "https://discord.gg/aEkzE59\n"
                 "<https://github.com/DamourYouKnow/HAHA-NO-UR/issues>\n\n"
                 "Feel free to add this bot to your own server or host "
                 "your own version of it. If you are interested in "
                 "contributing to the bot please contact me. "
                 "I'm willing to teach so don't worry about not having any "
                 "programming experience.")
        await self.bot.say(reply)

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

    @commands.command()
    async def ping(self):
        """
        ping command
        """
        start_time = time()
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = time()
        await self.bot.edit_message(
            msg, 'Pong! | :timer: {}ms'.format(
                round((end_time - start_time) * 1000))
        )
