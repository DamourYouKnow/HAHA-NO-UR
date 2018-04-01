from collections import namedtuple
from posixpath import basename
from random import randint, shuffle, uniform
from time import time
from urllib.parse import urlsplit

from discord import User

from bot import HahaNoUR
from core.argument_parser import parse_arguments
from core.image_generator import create_image, get_one_img, \
    idol_img_path

RATES = {
    "regular": {"N": 0.95, "R": 0.05, "SR": 0.00, "SSR": 0.00, "UR": 0.00},
    "honour": {"N": 0.00, "R": 0.80, "SR": 0.15, "SSR": 0.04, "UR": 0.01},
    "coupon": {"N": 0.00, "R": 0.00, "SR": 0.80, "SSR": 0.00, "UR": 0.20},
    "support": {"N": 0.00, "R": 0.60, "SR": 0.30, "SSR": 0.00, "UR": 0.10},
    "alpaca": {"N": 0.00, "R": 0.85, "SR": 0.15, "SSR": 0.00, "UR": 0.00}
}


class ScoutImage(namedtuple('ScoutImage', ('bytes', 'name'))):
    __slots__ = ()


class ScoutHandler:
    """
    Provides scouting functionality for bot.
    """
    __slots__ = ('results', '_bot', '_user', '_box', '_count',
                 '_guaranteed_sr', '_args')

    def __init__(self, bot: HahaNoUR, user: User,
                 box: str = "honour", count: int = 1,
                 guaranteed_sr: bool = False, args: tuple = ()):
        """
        Constructor for a Scout.
        :param session_manager: the SessionManager.
        :param user: User requesting scout.
        :param box: Box to scout in (honour, regular, coupon).
        :param count: Number of cards in scout.
        :param guaranteed_sr: Whether the scout will roll at least one SR.
        :param args: Scout command arguments
        """
        self.results = []
        self._bot = bot
        self._user = user
        self._box = box
        self._count = count
        self._guaranteed_sr = guaranteed_sr
        self._args = parse_arguments(self._bot, args, True)

    async def do_scout(self):
        if self._count > 1:
            return await self._handle_multiple_scout()
        else:
            return await self._handle_solo_scout()

    async def _handle_multiple_scout(self):
        """
        Handles a scout with multiple cards

        :return: Path of scout image
        """
        cards = await self._scout_cards()

        if len(cards) != self._count:
            self.results = []
            return None

        fname = f'{int(time())}{randint(0, 100)}.png'
        _bytes = await create_image(self._bot.session_manager, cards, 2)
        return ScoutImage(_bytes, fname)

    async def _handle_solo_scout(self):
        """
        Handles a solo scout

        :return: Path of scout image
        """
        card = await self._scout_cards()

        # Send error message if no card was returned
        if not card:
            self.results = []
            return None

        card = card[0]

        if card["card_image"] is None:
            url = "https:" + card["card_idolized_image"]
        else:
            url = "https:" + card["card_image"]

        fname = basename(urlsplit(url).path)
        image_path = idol_img_path.joinpath(fname)
        bytes_ = await get_one_img(
            url, image_path, self._bot.session_manager)
        return ScoutImage(bytes_, fname)

    async def _scout_cards(self) -> list:
        """
        Scouts a specified number of cards

        :return: cards scouted
        """
        rarities = []

        if self._guaranteed_sr:
            for r in range(self._count - 1):
                rarities.append(self._roll_rarity())

            if rarities.count("R") + rarities.count("N") == self._count - 1:
                rarities.append(self._roll_rarity(True))
            else:
                rarities.append(self._roll_rarity())

        # Case where a normal character is selected
        elif (self._box == "regular") \
                and len(self._args["name"]) > 0:
            for r in range(self._count):
                rarities.append("N")

        else:
            for r in range(self._count):
                rarities.append(self._roll_rarity())

        results = []

        for rarity in RATES[self._box].keys():
            if rarities.count(rarity) > 0:
                scout = await self._scout_request(
                    rarities.count(rarity), rarity
                )

                results += _get_adjusted_scout(
                    scout, rarities.count(rarity)
                )

        self.results = results
        shuffle(results)
        return results

    async def _scout_request(self, count: int, rarity: str) -> dict:
        """
        Scouts a specified number of cards of a given rarity

        :param rarity: Rarity of all cards in scout

        :return: Cards scouted
        """
        if count == 0:
            return []
        params = {
            'rarity': rarity,
            'is_promo': False,
            'is_special': (self._box == 'support')
        }

        for arg_type, arg_values in self._args.items():
            if not arg_values:
                continue

            val = arg_values

            # Comma seperated strings need to use $in.
            if len(arg_values) > 0:
                val = {'$in': arg_values}

            if arg_type == "main_unit":
                params['idol.main_unit'] = val
            elif arg_type == "sub_unit":
                params['idol.sub_unit'] = val
            elif arg_type == "name":
                params['idol.name'] = val
            elif arg_type == "year":
                params['idol.year'] = val
            elif arg_type == "attribute":
                params['attribute'] = val

        # Get and return response
        return await self._bot.db.cards.get_random_cards(params, count)

    def _roll_rarity(self, guaranteed_sr: bool = False) -> str:
        """
        Generates a random rarity based on the defined scouting rates

        :param guaranteed_sr: Whether roll should be an SR

        :return: rarity represented as a string ('UR', 'SSR', 'SR', 'R')
        """
        roll = uniform(0, 1)

        required_roll = RATES[self._box]['UR']
        if roll < required_roll:
            return 'UR'

        required_roll = RATES[self._box]['SSR'] + RATES[self._box]['UR']
        if roll < required_roll:
            return 'SSR'

        required_roll = RATES[self._box]['SR'] + RATES[self._box]['SSR']
        required_roll += RATES[self._box]['UR']
        if roll < required_roll:
            return 'SR'

        required_roll = RATES[self._box]['R'] + RATES[self._box]['SR']
        required_roll += RATES[self._box]['SSR'] + RATES[self._box]['UR']
        if roll < required_roll:
            if guaranteed_sr:
                return 'SR'
            else:
                return 'R'
        else:
            return 'N'


def _get_adjusted_scout(scout: list, required_count: int) -> list:
    """
    Adjusts a pull of a single rarity by checking if a card should flip to
    a similar one and by duplicating random cards in the scout if there were
    not enough scouted.
    :param scout: List representing the scout.
        All these cards will have the same rarity.
    :param required_count: The number of cards that need to be scouted.
    :return: Adjusted list of cards scouted
    """
    # Add missing cards to scout by duplicating random cards already present
    current_count = len(scout)

    # Something bad happened, return an empty list
    if current_count == 0:
        return []

    pool_size = current_count
    while current_count < required_count:
        scout.append(
            scout[randint(0, pool_size - 1)]
        )
        current_count += 1

    # Traverse scout and roll for flips
    for card_index in range(len(scout) - 1):
        # for each card there is a (1 / total cards)
        # chance that we should dupe
        # the previous card
        roll = uniform(0, 1)
        if roll < 1 / len(scout):
            scout[card_index] = scout[card_index + 1]

    return scout