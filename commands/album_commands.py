from os import remove
from discord.ext import commands
from bot import HahaNoUR
import math
from time import clock
from random import randint
from get_names import get_idol_names
from image_generator import create_image
from discord import User
from aliases import ALIASES

PAGE_SIZE = 12
IDOL_NAMES = get_idol_names()
SORTS = ["id", "name", "attribute", "rarity"]
RARITIES = ["UR", "SSR", "SR", "R", "N"]
ATRIBUTES = ["Smile", "Pure", "Cool"]

# Dictionary mapping user ids to last used album arguments
_last_user_args = {}


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

    async def __handle_result(self, ctx, album_size, image_path, delete=True):
        if not image_path:
            await self.__send_error_msg(ctx)
        else:
            page = _last_user_args[ctx.message.author.id]["page"]
            max_page = int(math.ceil(album_size / PAGE_SIZE))
            msg = '<@' + ctx.message.author.id + '> '
            msg += "Page " + str(page + 1) + " of " + str(max_page)
            await self.bot.upload(
                image_path, content=msg)

            if delete:
                remove(image_path)

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def album(self, ctx, *args: str):
        user = ctx.message.author
        album = self.bot.db.get_user_album(user)
        _parse_arguments(args, user)
        print(_last_user_args[user.id]["filter_type"])
        print(_last_user_args[user.id]["filter_value"])
        print(_last_user_args[user.id]["sort"])
        album = _apply_filter(album, user)
        album = _apply_sort(album, user)
        album_size = len(album)
        album = _splice_page(album, user)

        urls = []
        for card in album:
            if card["round_card_image"] is None:
                urls.append("http:" + card["round_card_idolized_image"])
            else:
                urls.append("http:" + card["round_card_image"])

        # TODO change this to call newer version of function that makes labels.
        if len(urls) > 0:
            image_path = await create_image(
                    urls, 2, str(clock()) + str(randint(0, 100)) + ".png")
        else:
            image_path = None

        await self.__handle_result(ctx, album_size, image_path)

def _apply_filter(album: list, user: User):
    """
    Applys a user's filters to a card album, removing anything not matching
        the filter.

    :param album: Album being filtered.
    :param user: User who requested the album.

    :return: Filtered album.
    """
    filter_type = _last_user_args[user.id]["filter_type"]
    filter_value = _last_user_args[user.id]["filter_value"]

    if filter_type == None:
        return album

    # Looping backwards since we are removing elements
    for i in range(len(album) - 1, -1, -1):
        if album[i][filter_type] != filter_value:
            album.pop(i)

    return album


def _apply_sort(album: list, user: User) -> list:
    """
    Applys a user's sort to a card album.

    :param album: Album being sorted.
    :param user: User who requested the album.

    :return: Sorted album.
    """
    sort = _last_user_args[user.id]["sort"]

    if sort == "rarity":
        album.sort(key=lambda x: RARITIES.index(x["rarity"]))
    elif sort == "attribute":
        album.sort(key=lambda x: ATRIBUTES.index(x["attribute"]))
    elif sort == "name":
        album.sort(key=lambda x: k["name"])

    return album


def _splice_page(album: list, user: User) -> list:
    """
    Splices a user's last requested page out of their album.

    :param album: Album being spliced
    :param user: User who requested the album.

    :return: Spliced album.
    """
    page = _last_user_args[user.id]["page"]
    max_page = int(math.ceil(len(album) / PAGE_SIZE)) - 1

    if page > max_page:
        page = max_page
    if page < 0:
        page = 0
    _last_user_args[user.id]["page"] = page

    start = PAGE_SIZE * page
    end = (PAGE_SIZE * page) + PAGE_SIZE
    return album[start:end]


def _parse_arguments(args: tuple, user: User):
    """
    Parse arguments to get how an album will be sorted and filtered. The parsed
        arguments are stored in the user's last used arguments dictionary.

    :param args: Tuple of arguments.
    :param user: User who requested the album.
    """
    # Add user to last used argument dictionary if they don't already exist.
    if not user.id in _last_user_args:
        _last_user_args[user.id] = {
            "page": 0,
            "filter_type": None, # Filter "all" if None
            "filter_value": None,
            "sort": None # Sort by ID if None
        }

    # Get values of user's last album preview.
    page = _last_user_args[user.id]["page"]
    filter_type = _last_user_args[user.id]["filter_type"]
    filter_value = _last_user_args[user.id]["filter_value"]
    sort = _last_user_args[user.id]["sort"]

    # Parse arguments
    for arg in args:
        arg = arg.lower()

        # Parse page number
        if _is_number(arg):
            # -1 since we start indexing at 0.
            page = int(arg) - 1

        # Parse filters
        if arg == "all":
            filter_type = None
            filter_value = None

        if arg.upper() in RARITIES:
            filter_type = "rarity"
            filter_value = arg.upper()

        if arg.title() in ATRIBUTES:
            filter_type = "attribute"
            filter_value = arg.title()

        # Check for names
        for full_name in IDOL_NAMES:
            name_split = full_name.split(" ")

            # Check if name is exact match
            if arg.title() == name_split[-1]:
                filter_type = "name"
                filter_value = full_name

        for key in ALIASES["name"]:
            if arg in key:
                filter_type = "name"
                filter_value = ALIASES["name"][key].title()

        # Parse sort
        if arg in SORTS:
            _last_user_args[user.id]["sort"] = arg

        _last_user_args[user.id]["page"] = page
        _last_user_args[user.id]["filter_type"] = filter_type
        _last_user_args[user.id]["filter_value"] = filter_value
        _last_user_args[user.id]["sort"] = sort


def _is_number(string: str) -> bool:
    """
    Checks if a string is a valid number.

    :param string: String being tested.

    :return: True if valid number, otherwise false.
    """
    try:
        int(string)
        return True
    except ValueError:
        return False
