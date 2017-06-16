from os import remove
from discord.ext import commands
from bot import HahaNoUR
from aliases import ALIASES

PAGE_SIZE = 32
IDOL_NAMES = get_idol_names()
SORTS = ["id", "name", "attribute", "rarity"]
RARITIES = ["UR", "SSR", "SR", "R", "N"]
ATRIBUTES = ["smile", "pure", "cool"]

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

    async def __handle_result(self, ctx, results, image_path, delete=True):
        raise NotImplementedError

    @commands.command(pass_context=True)
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    async def __album(self, ctx, *args: str):
        # TODO find first number to use as page.
        raise NotImplementedError
        user = ctx.message.author
        album = self.bot.db.get_user_album(user)
        _parse_arguments(args, user)
        _apply_filter(album, user)
        _apply_sort(album, user)
        _splice_page(album, user)


def _apply_filter(album: list, user: User) -> list:
    """
    Applys a user's filters to a card album, removing anything not matching
        the filter.

    :param album: Album being sorted.
    :param user: User who requested the album.
    """
    filter_type = _last_user_args[user.id]["filter_type"]
    filter_value = _last_user_args[user.id]["filter_value"]

    # Looping backwards since we are removing elements
    for i in range(len(album) - 1, -1, -1):
        if album[i][filter_type] == filter_value:
            album.pop(i)


def _apply_sort(album: list, user: User):
    raise NotImplementedError


def _splice_page(album: list, user: User):
    """
    Splices a user's last requested page out of their album.

    :param album: Album being spliced
    :param user: User who requested the album.
    """
    page = _last_user_args[user.id]["page"]
    start = PAGE_SIZE * page
    end = (PAGE_SIZE * page) + PAGE_SIZE
    album = album[start:end]


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
            _last_user_args[user.id]["page"] = int(arg) - 1

        # Parse filters
        if arg == "all":
            filter_type = None
            filter_value = None

        if arg in RARITIES:
            filter_type = "rarity"
            filter_value = arg.upper()

        if arg in ATRIBUTES:
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
                filter_value = ALIASES["name"][arg].title()

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
