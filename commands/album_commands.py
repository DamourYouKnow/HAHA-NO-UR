from os import remove
from discord.ext import commands
from bot import HahaNoUR
from album import Album

class AlbumCommands:
    """
    A class to hold all album commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __send_error_msg(self, ctx):
        await self.bot.send_message(
            ctx.message.channel,
            '<@' + ctx.message.author.id + '> A transmission error occured.')

    async def __handle_result(self, ctx, results, image_path, delete=True):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def __album(self, ctx, *args: str):
        # TODO find first number to use as page.
        raise NotImplementedError


# TODO Functions for getting album previews.
# These will include parsing arguments to apply filters and sort rules.
