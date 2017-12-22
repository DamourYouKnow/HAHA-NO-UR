import discord
from discord.ext import commands
from core.checks import check_mongo
from bot import HahaNoUR

class Trivia:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(check_mongo)
    async def trivia(self, ctx, *args: str):
        """
        Description: |
            Find out how you can help contribute to the trivia module.
        """
        user = ctx.message.author
        msg = 'We need your help to crowdsource questions for an upcoming '
        msg += 'trivia module <https://goo.gl/forms/4IZL2yW1lJSQSmcu1>'       
        await self.bot.send_message(ctx.message.channel, msg)
