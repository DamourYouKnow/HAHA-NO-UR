import math
from operator import itemgetter

from discord import User
from discord.ext import commands

from bot import HahaNoUR
from core.argument_parser import parse_arguments
from core.checks import check_mongo
from core.get_names import get_idol_names
from core.image_generator import create_image

PAGE_SIZE = 16
ROWS = 4
IDOL_NAMES = get_idol_names()
SORTS = [
    'id',
    'name',
    'attribute',
    'rarity',
    'year',
    'date',
    'unit',
    'subunit',
    'newest'
]

# Dictionary mapping user ids to last used album arguments
_last_user_args = {}


class Album:
    """
    A class to hold all album commands.
    """

    def __init__(self, bot: HahaNoUR):
        self.bot = bot

    async def __send_error_msg(self, ctx):
        await self.bot.send_message(
            ctx.message.channel,
            f'<@{ctx.message.author.id }> No matching cards found.'
        )

    async def __handle_result(self, ctx, album_size, image):
        if not image:
            await self.__send_error_msg(ctx)
            _last_user_args[ctx.message.author.id] = _get_new_user_args()
        else:
            page = _last_user_args[ctx.message.author.id]["page"]
            max_page = int(math.ceil(album_size / PAGE_SIZE))
            msg = (f'<@{ctx.message.author.id}> Page {page+1} of {max_page}. '
                   f'`!help album` for more info.')
            await self.bot.upload(image, filename='a.png', content=msg)

    @commands.command(pass_context=True, aliases=['a'])
    @commands.cooldown(rate=3, per=2.5, type=commands.BucketType.user)
    @commands.check(check_mongo)
    async def album(self, ctx, *args: str):
        """
        Description: |
            View your album.

            Your selected filters and sort will be remembered.
            To clear filters, provide the argument <all>

        Optional Arguments: |
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
        filtered_album_size = len(album)
        album = _apply_sort(album, user)
        album = _splice_page(album, user)

        image = await create_image(
            self.bot.session_manager, album, ROWS, True, True
        ) if len(album) > 0 else None
        await self.__handle_result(ctx, filtered_album_size, image)


def _apply_filter(album: list, user: User):
    """
    Applys a user's filters to a card album, removing anything not matching
        the filter.

    :param album: Album being filtered.
    :param user: User who requested the album.

    :return: Filtered album.
    """
    filters = _last_user_args[user.id]['filters']

    for filter_type in filters:
        filter_values = filters[filter_type]

        if not filter_values:
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
    sort = _last_user_args[user.id]['sort']

    # FIXME This var doesn't seem to have any use.
    order = _last_user_args[user.id]['order']

    if not sort:
        return album
    if sort == 'date':
        sort = 'release_date'
    if sort == 'unit':
        sort = 'main_unit'
    if sort == 'subunit':
        sort = 'sub_unit'
    if sort == 'newest':
        sort = 'time_aquired'

    sort_descending = sort in [
        'rarity',
        'attribute',
        'release_date',
        'time_aquired',
        'main_unit',
        'sub_unit'
    ]

    return sorted(album, key=itemgetter(sort, 'id'), reverse=sort_descending)


def _splice_page(album: list, user: User) -> list:
    """
    Splices a user's last requested page out of their album.

    :param album: Album being spliced
    :param user: User who requested the album.

    :return: Spliced album.
    """
    page = _last_user_args[user.id]['page']
    max_page = int(math.ceil(len(album) / PAGE_SIZE)) - 1

    if page > max_page:
        page = max_page
    if page < 0:
        page = 0
    _last_user_args[user.id]['page'] = page

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
    if user.id not in _last_user_args:
        _last_user_args[user.id] = _get_new_user_args()

    # Get values of user's last album preview.
    page = _last_user_args[user.id]['page']
    filters = _last_user_args[user.id]['filters']
    sort = _last_user_args[user.id]['sort']

    # FIXME This var doesn't seem to have any use.
    order = _last_user_args[user.id]['order']

    new_filters = parse_arguments(args, True)
    if _has_filter(new_filters):
        filters = new_filters

    # Parse other arguments
    for arg in args:
        arg = arg.lower()

        # Reset filter if "all" is given
        if arg == 'all':
            filters = {
                'name': [],
                'main_unit': [],
                'sub_unit': [],
                'year': [],
                'attribute': [],
                'rarity': []
            }

        # Parse sort
        if arg in SORTS:
            sort = arg
            page = 0

        # Parse sort order
        if arg in ('+', '-'):
            # FIXME This var doesn't seem to have any use.
            order = arg

        # Parse if page number
        if _is_number(arg):
            page = int(arg) - 1

        _last_user_args[user.id]['page'] = page
        _last_user_args[user.id]['filters'] = filters
        _last_user_args[user.id]['sort'] = sort


def _get_new_user_args():
    args = {
        'page': 0,
        'filters': {
            'name': [],
            'main_unit': [],
            'sub_unit': [],
            'year': [],
            'attribute': [],
            'rarity': []
        },
        'sort': None,
        'order': None  # Sort by ID if None
    }
    return args


def _has_filter(filters: dict) -> bool:
    """
    Checks if a filter dictionary has any active filters.

    :param filters: Target filter dictionary.

    :return: True if target has filters, otherwise False.
    """
    return any(filters.values())


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
