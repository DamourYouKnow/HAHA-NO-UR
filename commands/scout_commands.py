from os import remove

from discord.ext import commands

from bot import HahaNoUR
from scout import Scout


class ScoutCommands:
    """
    A class to hold all bot commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __send_error_msg(self, ctx):
        await self.bot.send_message(
            ctx.message.channel,
            '<@' + ctx.message.author.id + '> A transmission error occured.')

    async def __handle_result(self, ctx, res, delete=True):
        if not res:
            await self.__send_error_msg(ctx)
        else:
            await self.bot.upload(
                res, content='<@' + ctx.message.author.id + '>')
            if delete:
                remove(res)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def scout(self, ctx, *args: str):
        """
        Command to do a solo scout
        """
        scout = Scout("honour", 1, False, args)
        res = await scout.do_scout()
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def scout11(self, ctx, *args: str):
        """
        Command do scout 11
        """
        scout = Scout("honour", 11, True, args)
        res = await scout.do_scout()
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True, aliases=['scoutregular', 'scoutr'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def __scoutregular(self, ctx, *args: str):
        """
        Command to scout regular
        asdas
        asdasd
        asdasd
        asdasda
        sdasd
        """
        scout = Scout("regular", 1, False, args)
        res = await scout.do_scout()
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True, aliases=['scoutregular10', 'scoutr10'])
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def __scoutr10(self, ctx, *args: str):
        """
        Command to scout 10
        """
        scout = Scout("regular", 10, False, args)
        res = await scout.do_scout()
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True, aliases=['scoutcoupon', 'scoutc'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def __scoutc(self, ctx, *args: str):
        """
        Command to scout coupon
        """
        scout = Scout("coupon", 1, False, args)
        res = await scout.do_scout()
        await self.__handle_result(ctx, res)
