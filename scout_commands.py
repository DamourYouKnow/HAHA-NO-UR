from os import remove

from discord.ext import commands

from bot import HahaNoUR
from core import handle_multiple_scout, handle_solo_scout, parse_arguments


class Scout:
    """
    A class to hold all bot commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __send_error_msg(self, ctx):
        await self.bot.send_message(
            '<@' + ctx.message.author.id + '> A transmission error occured.')

    async def __handle_result(self, ctx, res, delete=False):
        if not res:
            await self.__send_error_msg(ctx)
        else:
            await self.bot.upload(
                res, content='<@' + ctx.message.author.id + '>')
            if delete:
                remove(res)

    @commands.command(aliases=['info', 'help'])
    async def _info(self):
        reply = "Instructions for how to use the bot can be found here:\n"
        "<https://github.com/DamourYouKnow/"
        "HAHA-NO-UR/blob/master/README.md>\n\n"
        "If you have any suggestions for new feautures or "
        "improvements contact D'Amour#2601 on discord or submit "
        "a request here:\n"
        "<https://github.com/DamourYouKnow/HAHA-NO-UR/issues>\n\n"
        "Feel free to add this bot to your own server or host "
        "your own version of it. If you are interested in "
        "contributing to the bot please contact me. "
        "I'm willing to teach so don't worry about not having any "
        "programming experience."
        await self.bot.say(reply)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def scout(self, ctx, *args: str):
        """
        Command to do a solo scout
        """
        unit, name = parse_arguments(self.bot.idol_names, args)
        res = await handle_solo_scout(self.bot.rates, 'honour', unit, name)
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def scout11(self, ctx, *args: str):
        """
        Command do scout 11
        """
        unit, name = parse_arguments(self.bot.idol_names, args)
        res = await handle_multiple_scout(
            ctx, self.bot.rates, 11, 'honour', unit, name)
        await self.__handle_result(ctx, res, True)

    @commands.command(pass_context=True, aliases=['scoutregular', 'scoutr'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def _scoutregular(self, ctx, *args: str):
        """
        Command to scout regular
        """
        unit, name = parse_arguments(self.bot.idol_names, args)
        res = await handle_solo_scout(self.bot.rates, "regular", None, name)
        await self.__handle_result(ctx, res)

    @commands.command(pass_context=True, aliases=['scoutregular10', 'scoutr10'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def _scoutr10(self, ctx, *args: str):
        """
        Command to scout 10
        """
        unit, name = parse_arguments(self.bot.idol_names, args)
        res = await handle_multiple_scout(
            ctx, self.bot.rates, 10, 'regular', None, name)
        await self.__handle_result(ctx, res, True)

    @commands.command(pass_context=True, aliases=['scoutcoupon', 'scoutc'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def _scoutc(self, ctx, *args: str):
        """
        Command to scout coupon
        """
        unit, name = parse_arguments(self.bot.idol_names, args)
        res = await handle_solo_scout(self.bot.rates, 'coupon', unit, name)
        await self.__handle_result(ctx, res)
