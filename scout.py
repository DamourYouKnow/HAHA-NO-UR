import urllib.parse
from pathlib import Path
from posixpath import basename
from random import randint, shuffle, uniform
from time import clock
from typing import Optional

from aiohttp import ClientConnectionError, ClientSession

from get_names import get_idol_names
from scout_image_generator import IDOL_IMAGES_PATH, create_image, \
    download_image_from_url

API_URL = 'http://schoolido.lu/api/'

RATES = {
    "regular": {"N": 0.95, "R": 0.05, "SR": 0.00, "SSR": 0.00,
                "UR": 0.00},
    "honour": {"N": 0.00, "R": 0.80, "SR": 0.15, "SSR": 0.04,
               "UR": 0.01},
    "coupon": {"N": 0.00, "R": 0.00, "SR": 0.80, "SSR": 0.00,
               "UR": 0.20}
}

IDOL_NAMES = get_idol_names()

ALIASES = {
    "name": {
        ("honk"): "kousaka honoka",
        ("eri"): "ayase eli",
        ("yohane"): "tsushima yoshiko",
        ("hana", "pana"): "koizumi hanayo",
        ("tomato"): "nishikino maki"
    },
    "main_unit": {
        ("muse", "µ's"): "µ's",
        ("aqours", "aquas", "aquors"): "aqours",
        ("a-rise", "arise"): "a-rise",
        ("saint", "snow"): "saint snow"
    },
    "sub_unit": {
        ("lily", "white"): "lily white",
        ("bibi"): "bibi",
        ("printemps"): "printemps",
        ("guilty", "kiss"): "guilty kiss",
        ("azalea"): "azalea",
        ("cyaron", "cyaron!", "crayon", "crayon!"): "cyaron!"
    }
}


def _get_adjusted_scout(scout: dict, required_count: int) -> list:
    """
    Adjusts a pull of a single rarity by checking if a card should flip to
    a similar one and by duplicating random cards in the scout if there were
    not enough scouted.

    :param scout: Dictionary representing the scout.
        All these cards will have the same rarity.

    :param required_count: The number of cards that need to be scouted.

    :return: Adjusted list of cards scouted
    """
    # Add missing cards to scout by duplicating random cards already present
    current_count = len(scout['results'])

    # Something bad happened, return an empty list
    if current_count == 0:
        return []

    while current_count < required_count:
        scout['results'].append(
            scout['results'][randint(0, current_count - 1)]
        )
        current_count += 1

    # Traverse scout and roll for flips
    for card_index in range(0, len(scout['results']) - 1):
        # for each card there is a (1 / total cards)
        # chance that we should dupe
        # the previous card
        roll = uniform(0, 1)
        if roll < 1 / scout['count']:
            scout['results'][card_index] = scout['results'][card_index + 1]

    return scout['results']


def _parse_arguments(args: tuple) -> tuple:
    """
    Parse user argument

    :param args: The user input to be parsed

    :return: A tuple of (arg_type, arg)
    """
    if len(args) > 0:
        arg = args[0].lower()
    else:
        arg = "none"

    arg_type = ""
    arg_value = ""

    # Check for names
    for full_name in IDOL_NAMES:
        name_split = full_name.split(" ")

        # Check if name is exact match
        if arg.title() == name_split[len(name_split) - 1]:
            arg_type = "name"
            arg_value = full_name
            break

    # Check for unit and idol names by alias
    for alias_dict in ALIASES:
        search_result = _resolve_alias(arg, ALIASES[alias_dict])
        print(search_result)
        if search_result != "":
            arg_type = alias_dict
            arg_value = search_result
            break

    # Check for years
    if arg in ["first", "second", "third"]:
        arg_type = "year"
        arg_value = arg

    # Check for attribute
    if arg in ["cool", "smile", "pure"]:
        arg_type = "attribute"
        arg_value = arg.title()

    # Check for names
    for full_name in IDOL_NAMES:
        name_split = full_name.split(" ")

        # Check if name is exact match
        if arg.title() == name_split[len(name_split) - 1]:
            arg_type = "name"
            arg_value = full_name
            break

    return arg_type, arg_value.replace(" ", "%20")


def _resolve_alias(target: str, alias_dict: dict) -> str:
    """
    Resolves an alias from a given alias dicitonary.

    :param target: Target string being searched for.
    :alias_dict: Alias dicitonary being searched in.

    :return: Alias result if found, otherwise returns an empty string.
    """
    for key in alias_dict:
        if isinstance(key, str) and target == key:
            return alias_dict[key]

        if isinstance(key, tuple) and target in key:
            return alias_dict[key]

    return ""


class Scout:
    """
    Provides scouting functionality for bot.
    """

    def __init__(self, box: str = "honour", count: int = 1,
                 guaranteed_sr: bool = False, args: tuple = ()):
        """
        Constructor for a Scout.

        :param box: Box to scout in (honour, regular, coupon).
        :param count: Number of cards in scout.
        :param args: Scout command arguments
        """
        self._box = box
        self._count = count
        self._guaranteed_sr = guaranteed_sr
        self._arg_type, self._arg_value = _parse_arguments(args)

    async def do_scout(self):
        if self._count > 1:
            return await self._handle_multiple_scout()
        else:
            return await self._handle_solo_scout()

    async def _handle_multiple_scout(self) -> Optional[str]:
        """
        Handles a scout with multiple cards

        :return: Path of scout image
        """
        if self._box == "honour":
            cards = await self._scout_cards()
        else:
            cards = await self._scout_cards()

        circle_image_urls = []

        for card in cards:
            if card["round_card_image"] is None:
                circle_image_urls.append(
                    "http:" + card["round_card_idolized_image"]
                )
            else:
                circle_image_urls.append("http:" + card["round_card_image"])

        if len(circle_image_urls) != self._count:
            return

        image_path = await create_image(
            circle_image_urls,
            2,
            str(clock()) + str(randint(0, 100)) + ".png"
        )

        return image_path

    async def _handle_solo_scout(self) -> Optional[Path]:
        """
        Handles a solo scout

        :return: Path of scout image
        """
        card = await self._scout_cards()

        # Send error message if no card was returned
        if len(card) == 0:
            return None

        card = card[0]

        if card["card_image"] is None:
            url = "http:" + card["card_idolized_image"]
        else:
            url = "http:" + card["card_image"]

        image_path = IDOL_IMAGES_PATH.joinpath(
            basename(urllib.parse.urlsplit(url).path))
        session = ClientSession()
        await download_image_from_url(url, image_path, session)
        session.close()

        return image_path

    async def _scout_cards(self) -> list:
        """
        Scouts a specified number of cards

        :return: cards scouted
        """
        rarities = []

        if self._guaranteed_sr:
            for r in range(0, self._count - 1):
                rarities.append(self._roll_rarity())

            if rarities.count("R") + rarities.count("N") == self._count - 1:
                rarities.append(self._roll_rarity(True))
            else:
                rarities.append(self._roll_rarity())

        # Case where a normal character is selected
        elif self._box == "regular" and self._arg_type == "name":
            for r in range(0, self._count):
                rarities.append("N")

        else:
            for r in range(0, self._count):
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

        shuffle(results)
        return results

    async def _scout_request(self, count: int, rarity: str) -> dict:
        """
        Scouts a specified number of cards of a given rarity

        :param rarity: Rarity of all cards in scout

        :return: Cards scouted
        """
        if count == 0:
            return {}

        # Build request url
        request_url = \
            API_URL + 'cards/?rarity=' + rarity \
            + '&ordering=random&is_promo=False&is_special=False'

        if self._arg_type == "main_unit":
            request_url += '&idol_main_unit=' + self._arg_value
        elif self._arg_type == "sub_unit":
            request_url += '&idol_sub_unit=' + self._arg_value
        elif self._arg_type == "name":
            request_url += "&name=" + self._arg_value
        elif self._arg_type == "year":
            request_url += "&idol_year=" + self._arg_value
        elif self._arg_type == "attribute":
            request_url += "&attribute=" + self._arg_value

        request_url += '&page_size=' + str(count)

        # Get and return response
        async with ClientSession() as session:
            async with session.get(request_url) as response:
                if response.status != 200:
                    raise ClientConnectionError
                response_json = await response.json()
                return response_json

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
