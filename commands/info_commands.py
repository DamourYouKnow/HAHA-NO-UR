from discord.ext import commands

from bot import HahaNoUR


class InfoCommands:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command()
    async def info(self):
        # TODO D'Amour read this from file.
        reply = "Instructions for how to use the bot can be found here:\n"
        reply += "<https://github.com/DamourYouKnow/"
        reply += "HAHA-NO-UR/blob/master/README.md>\n\n"
        reply += "If you have any suggestions for new feautures or "
        reply += "improvements contact D'Amour#2601 on discord or submit "
        reply += "a request here:\n"
        reply += "<https://github.com/DamourYouKnow/HAHA-NO-UR/issues>\n\n"
        reply += "Feel free to add this bot to your own server or host "
        reply += "your own version of it. If you are interested in "
        reply += "contributing to the bot please contact me. "
        reply += "I'm willing to teach so don't worry about not having any "
        reply += "programming experience."
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
