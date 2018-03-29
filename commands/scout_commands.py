from discord.ext import commands

from bot import HahaNoUR
from core.scout_handler import ScoutHandler, ScoutImage
from core.checks import check_mongo


class Scout:
    """
    A class to hold all Scout commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __handle_result(self, ctx, results, image: ScoutImage):
        """
        Handle a scout result.
        :param ctx: the context.
        :param results: the scout results.
        :param image: scout image result.
        """
        if not image:
            msg = (f'<@{ctx.message.author.id}> '
                   f'A transmission error occured. No cards found!')
            await self.bot.say(msg)
            return
        await self.bot.upload(
            image.bytes, filename=image.name,
            content=f'<@{ctx.message.author.id}>'
        )

        if not await self.bot.db.users.find_user(ctx.message.author.id):
            await self.bot.db.users.insert_user(ctx.message.author.id)
        await self.bot.db.users.add_to_user_album(
                ctx.message.author.id, results)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scout(self, ctx, *args: str):
        """
        Description: |
            Solo honour scouting.

            **Rates:** R: 80%, SR: 15%, SSR: 4%, UR: 1%
        Optional Arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'honour', 1, False, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scout11(self, ctx, *args: str):
        """
        Description: |
            10+1 honour scouting.

            **Rates:** R: 80%, SR: 15%, SSR: 4%, UR: 1%
        Optional Arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'honour', 11, True, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)

    @commands.command(pass_context=True, aliases=['scoutr'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scoutregular(self, ctx, *args: str):
        """
        Description: |
            Solo regular scouting.

            **Rates:** N: 95%, R: 5%
        Optional Arguments: |
            Attribute (smile, pure, cool)
            Idol first name (Honoka, Chika, ...)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'regular', 1, False, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)

    @commands.command(pass_context=True, aliases=['scoutr10'])
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scoutregular10(self, ctx, *args: str):
        """
        Description: |
            10 card regular scouting.

            **Rates:** N: 95%, R: 5%
        Optional Arguments: |
            Attribute (smile, pure, cool)
            Idol first name (Honoka, Chika, ...)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'regular', 10, False, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)

    @commands.command(pass_context=True, aliases=['scoutc'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scoutcoupon(self, ctx, *args: str):
        """
        Description: |
            Blue scouting coupon scouting.

            **Rates:** SR: 80%, UR: 20%
        Optional Arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'coupon', 1, False, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)


    @commands.command(pass_context=True, aliases=['scouts'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def scoutsupport(self, ctx, *args: str):
        """
        Description: |
            Support scouting.

            **Rates:** R: 60%, SR: 30%, UR: 10%
        Optional Arguments: |
            Attribute (smile, pure, cool)
            Idol first name (Honoka, Chika, ...)
            Year (first, second, third)
        """
        scout = ScoutHandler(
            self.bot, ctx.message.author, 'support', 1, False, args)
        image = await scout.do_scout()
        await self.__handle_result(ctx, scout.results, image)
