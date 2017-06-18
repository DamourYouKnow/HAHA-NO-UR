from os import remove
from discord.ext import commands
from bot import HahaNoUR
import math
from time import clock
from random import randint
from get_names import get_idol_names
from argument_parser import parse_arguments
from image_generator import create_image
from discord import User
from operator import itemgetter

PAGE_SIZE = 16
ROWS = 4
IDOL_NAMES = get_idol_names()
SORTS = [
    "id",
    "name",
    "attribute",
    "rarity",
    "year",
    "date",
    "unit",
    "subunit",
    "newest"
]

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
            msg += "Page " + str(page + 1) + " of " + str(max_page) + ". "
            msg += "`!help album` for more info."
            await self.bot.upload(
                image_path, content=msg)

            if delete:
                remove(image_path)

    @commands.command(pass_context=True, aliases=['album', 'a'])
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def __album(self, ctx, *args: str):
        """
        general: |
            View your album.

            Your selected filters and sort will be remembered.
            To clear filters, provide the argument <all>

        optional arguments: |
            Page (1, 2, 3, ...)
            Sort (id, rarity, newest, attribute, year, unit, subunit, date)
            Main unit name (Aqours, Muse, Saint Snow, A-RISE)
            Sub unit name (Lily White, CYaRon, ...)
            Idol first name (Honoka, Chika, ...)
            Attribute (smile, pure, cool)
            Year (first, second, third)
            Rarity (UR, SSR, SR, R, N)
        """
        user = ctx.message.author
        album = self.bot.db.get_user_album(user)
        _parse_album_arguments(args, user)
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
                    urls,
                    ROWS,
                    str(clock()) + str(randint(0, 100)) + ".png",
                    align=True)
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
    filters = _last_user_args[user.id]["filters"]

    for filter_type in filters:
        filter_values = filters[filter_type]

        if len(filter_values) == 0:
            continue

        # Looping backwards since we are removing elements
        for i in range(len(album) - 1, -1, -1):
            # Generic case
            if album[i][filter_type] not in filter_values:
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
    order = _last_user_args[user.id]["order"]

    if sort == None:
        return album
    if sort == "date":
        sort = "release_date"
    if sort == "unit":
        sort = "main_unit"
    if sort == "subunit":
        sort = "sub_unit"
    if sort == "newest":
        sort = "time_aquired"

    sort_descending = sort in [
            "rarity",
            "attribute",
            "release_date",
            "time_aquired",
            "main_unit",
            "sub_unit"
        ]

    album = sorted(album, key=itemgetter(sort, "id"), reverse=sort_descending)

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


def _parse_album_arguments(args: tuple, user: User):
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
            "filters": {
                "name": [],
                "main_unit": [],
                "sub_unit": [],
                "year": [],
                "attribute": [],
                "rarity": []
            },
            "sort": None,
            "order": None # Sort by ID if None
        }

    # Get values of user's last album preview.
    page = _last_user_args[user.id]["page"]
    filters = _last_user_args[user.id]["filters"]
    sort = _last_user_args[user.id]["sort"]
    order = _last_user_args[user.id]["order"]

    new_filters = parse_arguments(args, True)
    if _has_filter(new_filters):
        filters = new_filters

    # Parse other arguments
    for arg in args:
        arg = arg.lower()

        # Reset filter if "all" is given
        if arg == "all":
            filters = {
                "name": [],
                "main_unit": [],
                "sub_unit": [],
                "year": [],
                "attribute": [],
                "rarity": []
            }

        # Parse sort
        if arg in SORTS:
            sort = arg
            page = 0

        # Parse sort order
        if arg in ["+", "-"]:
            order = arg

        # Parse if page number
        if _is_number(arg):
            page = int(arg) - 1

        _last_user_args[user.id]["page"] = page
        _last_user_args[user.id]["filters"] = filters
        _last_user_args[user.id]["sort"] = sort

def _has_filter(filters: dict) -> bool:
    """
    Checks if a filter dictionary has any active filters.

    :param filters: Target filter dictionary.

    :return: True if target has filters, otherwise False.
    """
    for key in filters:
        if len(filters[key]) > 0:
            return True
    return False


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
