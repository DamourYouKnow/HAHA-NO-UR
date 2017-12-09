from discord.ext import commands
from core.checks import check_mongo
from bot import HahaNoUR

class Stats:
    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['stats'])
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def mystats(self, ctx, *args: str):
        """
        Description: |
            Provides stats about you.
        """
        raise NotImplementedError

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=30, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def botstats(self, ctx, *args: str):
        """
        Description: |
            Provides stats about the bot.
        """
        raise NotImplementedError
