import urllib.parse
from posixpath import basename
from random import randint, shuffle, uniform
from time import clock
from pathlib import Path
from discord import User

from bot import SessionManager
from core.argument_parser import parse_arguments
from core.get_names import get_idol_names
from core.image_generator import IDOL_IMAGES_PATH, create_image, \
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


class Scout:
    """
    Provides scouting functionality for bot.
    """

    def __init__(self, session_manager: SessionManager, user: User,
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
        self.image_path = None
        self.session_manager = session_manager
        self._user = user
        self._box = box
        self._count = count
        self._guaranteed_sr = guaranteed_sr
        self._args = parse_arguments(args)

    async def do_scout(self):
        if self._count > 1:
            await self._handle_multiple_scout()
        else:
            await self._handle_solo_scout()

        self.results = _shrink_results(self.results)

    async def _handle_multiple_scout(self):
        """
        Handles a scout with multiple cards

        :return: Path of scout image
        """
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
            self.results = []
            return None

        self.image_path = await create_image(
            self.session_manager,
            circle_image_urls,
            2,
            str(clock()) + str(randint(0, 100)) + ".png"
        )

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
            url = "http:" + card["card_idolized_image"]
        else:
            url = "http:" + card["card_image"]

        self.image_path = IDOL_IMAGES_PATH.joinpath(
            basename(urllib.parse.urlsplit(url).path))

        await download_image_from_url(url, Path(self.image_path),
                                      self.session_manager)

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
                and any("name" in arg for arg in self._args):
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
            return {}
        params = {
            'rarity': rarity,
            'ordering': 'random',
            'is_promo': 'False',
            'is_special': 'False',
            'page_size': str(count)
        }
        # Build request url
        request_url = API_URL + 'cards/?'

        for arg_type, arg_values in self._args.items():
            if not arg_values:
                continue

            values_str = ",".join(arg_values)
            values_str = values_str.replace(" ", "%20")

            if arg_type == "main_unit":
                values_str = values_str.replace("Muse", "µ's")
                params['idol_main_unit'] = values_str
            elif arg_type == "sub_unit":
                params['idol_sub_unit'] = values_str
            elif arg_type == "name":
                request_url += "&name=" + values_str
            # FIXME Why the heck does this not work.
            # elif arg_type == "name":
            #     params['name'] = values_str
            elif arg_type == "year":
                params['idol_year'] = values_str
            elif arg_type == "attribute":
                params['attribute'] = values_str

        # Get and return response
        return await self.session_manager.get_json(request_url, params)

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
    for card_index in range(len(scout['results']) - 1):
        # for each card there is a (1 / total cards)
        # chance that we should dupe
        # the previous card
        roll = uniform(0, 1)
        if roll < 1 / scout['count']:
            scout['results'][card_index] = scout['results'][card_index + 1]

    return scout['results']


def _shrink_results(results: list):
    """
    Removed uneeded information from scout results.

    :param results: Scout results being shrunk.
    """
    if not results:
        return

    # Remove dupes
    dupeless = []
    for card in results:
        if card not in dupeless:
            dupeless.append(card)
    results = dupeless

    keep_fields = {
        "id",
        "name",
        "year",
        "main_unit",
        "sub_unit",
        "rarity",
        "attribute",
        "release_date",
        "round_card_image",
        "round_card_idolized_image"
    }
    res = []
    for result in results:
        # Copy needed fields under idol
        result["name"] = result["idol"]["name"]
        result["year"] = result["idol"]["year"]
        result["main_unit"] = result["idol"]["main_unit"]
        result["sub_unit"] = result["idol"]["sub_unit"]

        # Delete uneeded fields
        delete_fields = []
        for field in result:
            if field not in keep_fields:
                delete_fields.append(field)
        for field in delete_fields:
            result.pop(field, None)

        # Replace None with empty string for sorting purposes.
        replaced = {key: (val or '') for key, val in result.items()}
        res.append(replaced)
    return res
