from logging import INFO
from pathlib import Path

from discord.ext import commands

from bot import HahaNoUR
from core.scout import Scout


class ScoutCommands:
    """
    A class to hold all bot commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __handle_result(self, ctx, results, image_path: Path, delete):
        """
        Handle a scout result.
        :param ctx: the context.
        :param results: the scout results.
        :param image_path: the path to the image.
        :param delete: delete the image or not.
        """
        if image_path is None:
            msg = "<@" + ctx.message.author.id + "> "
            msg += "A transmission error occured. No cards found!"
            await self.bot.say(msg)
            return
        await self.bot.upload(
            image_path, content='<@' + ctx.message.author.id + '>')

        # Add to database
        if not self.bot.db.find_user(ctx.message.author):
            self.bot.db.insert_user(ctx.message.author)
        self.bot.db.add_to_user_album(ctx.message.author, results)
        with Path(image_path) as f:
            if delete and f.is_file():
                self.bot.logger.log(INFO, 'Deleting {}'.format(image_path))
                f.unlink()

    @commands.command(pass_context=True)
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def scout(self, ctx, *args: str):
        """
        general: |
            Solo honour scouting.

            "**Rates:** R: 80%, SR: 15%, SSR: 4%, UR: 1%"
        optional arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = Scout(
            self.bot.session_manager,
            ctx.message.author, "honour", 1, False, args
        )
        await scout.do_scout()
        await self.__handle_result(ctx, scout.results, scout.image_path, False)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def scout11(self, ctx, *args: str):
        """
        general: |
            10+1 honour scouting.

            "**Rates:** R: 80%, SR: 15%, SSR: 4%, UR: 1%"
        optional arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = Scout(
            self.bot.session_manager,
            ctx.message.author, "honour", 11, True, args
        )
        await scout.do_scout()
        await self.__handle_result(ctx, scout.results, scout.image_path, True)

    @commands.command(pass_context=True, aliases=['scoutregular', 'scoutr'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def __scoutregular(self, ctx, *args: str):
        """
        general: |
            Solo regular scouting.

            "**Rates:** N: 90%, R: 5%"
        optional arguments: |
            Attribute (smile, pure, cool)
        """
        scout = Scout(
            self.bot.session_manager,
            ctx.message.author, "regular", 1, False, args
        )
        await scout.do_scout()
        await self.__handle_result(ctx, scout.results, scout.image_path, False)

    @commands.command(pass_context=True, aliases=['scoutregular10', 'scoutr10'])
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def __scoutr10(self, ctx, *args: str):
        """
        general: |
            10 card regular scouting.True

            **Rates:** N: 90%, R: 5%
        optional arguments: |
            Attribute (smile, pure, cool)
        """
        scout = Scout(
            self.bot.session_manager,
            ctx.message.author, "regular", 10, False, args
        )
        await scout.do_scout()
        await self.__handle_result(ctx, scout.results, scout.image_path, True)

    @commands.command(pass_context=True, aliases=['scoutcoupon', 'scoutc'])
    @commands.cooldown(rate=5, per=2.5, type=commands.BucketType.user)
    async def __scoutc(self, ctx, *args: str):
        """
        general: |
            Blue scouting coupon scouting.

            "**Rates:** SR: 80%, UR: 20%"
        optional arguments: |
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
        """
        scout = Scout(
            self.bot.session_manager,
            ctx.message.author, "coupon", 1, False, args
        )
        await scout.do_scout()
        await self.__handle_result(ctx, scout.results, scout.image_path, False)
