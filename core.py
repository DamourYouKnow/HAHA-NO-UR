import urllib.parse
from posixpath import basename
from random import randint, shuffle, uniform
from time import clock

from aiohttp import ClientConnectionError, ClientSession

from scout_image_generator import IDOL_IMAGES_PATH, create_image, \
    download_image_from_url

API_URL = 'http://schoolido.lu/api/'


async def get_idol_names() -> list:
    """
    Gets a list of every idol name (Last First)

    :return: List of names
    """
    count_url = API_URL + 'idols'
    res_url = API_URL + 'idols/?page_size='

    async with ClientSession() as session:
        async with session.get(count_url) as count_response:
            if count_response.status != 200:
                return

            count = await count_response.json()
            count = count['count']

        async with session.get(res_url + str(count)) as result_response:
            if result_response.status != 200:
                return

            res_lst = await result_response.json()
            res_lst = res_lst['results']

    return [res['name'] for res in res_lst]


def roll_rarity(rates: dict, box: str, guaranteed_sr: bool=False) -> str:
    """
    Generates a random rarity based on the defined scouting rates

    :param rates: different scout rates, in a dict.

    :param box:

    :param guaranteed_sr: Whether an R will flip to an SR

    :return: rarity represented as a string ('UR', 'SSR', 'SR', 'R')
    """
    roll = uniform(0, 1)

    required_roll = rates[box]['UR']
    if roll < required_roll:
        return 'UR'

    required_roll = rates[box]['SSR'] + rates[box]['UR']
    if roll < required_roll:
        return 'SSR'

    required_roll = rates[box]['SR'] + rates[box]['SSR']
    required_roll += rates[box]['UR']
    if roll < required_roll:
        return 'SR'

    required_roll = rates[box]['R'] + rates[box]['SR']
    required_roll += rates[box]['SSR'] + rates[box]['UR']
    if roll < required_roll:
        if guaranteed_sr:
            return 'SR'
        else:
            return 'R'
    else:
        return 'N'


async def scout_request(count: int, rarity: str,
        unit: str=None, name: str=None) -> dict:
    """
    Scouts a specified number of cards of a given rarity

    :param count: Number of cards to scouted
    :param rarity: Rarity of all cards in scout
    :param unit: Unit of card to scout
    :param name: Name of idol to scout for

    :return: Cards scouted
    """
    if count == 0:
        return {}

    # Build request url
    request_url = \
        API_URL + 'cards/?rarity=' + rarity \
        + '&ordering=random&is_promo=False&is_special=False'

    if unit is not None:
        request_url += '&idol_main_unit=' + unit
    elif name is not None:
        names = name.split(' ')
        request_url += '&name=' + names[0]
        if len(names) == 2:
            request_url += '%' + '20' + names[1]

    request_url += '&page_size=' + str(count)

    # Get and return response
    async with ClientSession() as session:
        async with session.get(request_url) as response:
            if response.status != 200:
                raise ClientConnectionError
            response_json = await response.json()
            return response_json


def get_adjusted_scout(scout: dict, required_count: int) -> list:
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
        # for each card there is a (1 / total cards) chance that we should dupe
        # the previous card
        roll = uniform(0, 1)
        if roll < 1 / scout['count']:
            scout['results'][card_index] = scout['results'][card_index + 1]

    return scout['results']


async def scout_cards(
        rates: dict, count: int, box: str,
        guaranteed_sr: bool=False, unit: str=None, name: str=None) -> list:
    """
    Scouts a specified number of cards

    :param rates: Rates dictionary defining scout odds
    :param count: Number of cards to scouted
    :param box: Box being scouted in
    :param guaranteed_sr: Whether at least one card in the scout will be an SR
    :param unit: Unit of cards to scout
    :param name: Name of idol scout

    :return: cards scouted
    """
    rarities = []

    if guaranteed_sr:
        for r in range(0, count - 1):
            rarities.append(roll_rarity(rates, box))

        if rarities.count("R") + rarities.count("N") == count - 1:
            rarities.append(roll_rarity(rates, box, True))
        else:
            rarities.append(roll_rarity(rates, box))

    # Case where a normal character is selected
    elif box == "regular" and name is not None:
        for r in range(0, count):
            rarities.append("N")

    else:
        for r in range(0, count):
            rarities.append(roll_rarity(rates, box))

    results = []

    for rarity in rates[box].keys():
        if rarities.count(rarity) > 0:
            scout = await scout_request(
                rarities.count(rarity), rarity, unit, name
            )
            results += get_adjusted_scout(scout, rarities.count(rarity))
    shuffle(results)

    return results


async def handle_solo_scout(rates: dict, box: str,
        unit: str=None, name: str=None) -> str:
    """
    Handles a solo scout

    :param rates: Rates dictionary defining scout odds
    :param box: Box being scouted in ("regular", "honour", "coupon")
    :param unit: Name of unit being scouted for
    :param name: Name of idol being scouted for

    :return: Path of scout image
    """
    card = await scout_cards(rates, 1, box, False, unit, name)

    # Send error message if no card was returned
    if len(card) == 0:
        return None

    card = card[0]

    if card["card_image"] is None:
        url = "http:" + card["card_idolized_image"]
    else:
        url = "http:" + card["card_image"]

    image_path = IDOL_IMAGES_PATH + basename(urllib.parse.urlsplit(url).path)

    await download_image_from_url(url, image_path)

    return image_path

# TODO change how we give scout image a filename so we don't need to pass ctx
async def handle_multiple_scout(ctx: object, rates: dict, count: int, box: str,
        unit: str=None, name: str=None) -> str:
    """
    Handles a scout with multiple cards

    :param ctx: Message object from user requesting scout
    :param rates: Rates dictionary defining scout odds
    :param count: Number of cards to scout
    :param box: Box being scouted in ("regular", "honour", "coupon")
    :param unit: Name of unit being scouted for
    :param name: Name of idol being scouted for

    :return: Path of scout image
    """
    if box == "honour":
        cards = await scout_cards(rates, count, box, True, unit, name)
    else:
        cards = await scout_cards(rates, count, box, False, unit, name)

    circle_image_urls = []

    for card in cards:
        if card["round_card_image"] is None:
            circle_image_urls.append(
                "http:" + card["round_card_idolized_image"]
            )
        else:
            circle_image_urls.append("http:" + card["round_card_image"])

    if len(circle_image_urls) == 0:
        return

    image_path = await create_image(
        circle_image_urls,
        2,
        str(clock()) + ctx.message.author.id + ".png"
    )

    return image_path


def parse_arguments(idol_names: list, args: tuple) -> tuple:
    """
    Parse user input arguments and return the

    :param idol_names: The list of idol names
    :param args: The user input to be parsed

    :return: A tuple of (unit, name)
    """
    unit = None
    name = None

    for arg in args:
        if arg.lower() == "muse":
            unit = "µ's"
        elif arg.lower() == "aqours":
            unit = "aqours"


        for full_name in idol_names:
            name_split = full_name.split(" ")
            if arg.title() == name_split[len(name_split) - 1]:
                name = full_name
                break

    return unit, name
