import discord
import random
import json
import aiohttp
import requests
import asyncio
import os
import time
import math
import traceback
import threading
import posixpath
import urllib
import scout_image_generator
import idol_info
import logger

API_URL = "http://schoolido.lu/api/"

# Constants for scouting rates
RATES = {
    "regular": {"N": 0.95, "R": 0.05, "SR": 0.00, "SSR": 0.00, "UR": 0.00},
    "honour": {"N": 0.00, "R": 0.80, "SR": 0.15, "SSR": 0.04, "UR": 0.01},
    "coupon": {"N": 0.00, "R": 0.00, "SR": 0.80, "SSR": 0.00, "UR": 0.20}
}

# Other constants
IDOL_NAMES =  idol_info.get_idol_names()
MAIN_UNITS = ["µ's'", "aqours"]

# Used to handle rate limits
rate_limits = {}

client = discord.Client()

'''
Get the token and run the bot's main event loop
'''
def run_bot():
    # Get login token from text file and run client
    fp_token = open("token.txt", "r")
    token = fp_token.read().strip("\n")
    client.run(token)

'''
Generates a random rarity based on the defined scouting rates

guaranteed_sr: Boolean - Whether an R will flip to an SR

return: String - rarity represented as a string ("UR", "SSR", "SR", "R")
'''
def roll_rarity(box, guaranteed_sr = False):
    roll = random.uniform(0, 1)

    required_roll = RATES[box]["UR"]
    if roll < required_roll:
        return "UR"

    required_roll = RATES[box]["SSR"] + RATES[box]["UR"]
    if roll < required_roll:
        return "SSR"

    required_roll = RATES[box]["SR"] + RATES[box]["SSR"]
    required_roll += RATES[box]["UR"]
    if roll < required_roll:
        return "SR"

    required_roll = RATES[box]["R"] + RATES[box]["SR"]
    required_roll += RATES[box]["SSR"] + RATES[box]["UR"]
    if roll < required_roll:
        if guaranteed_sr:
            return "SR"
        else:
            return "R"

    else:
        return "N"

'''
Scouts a specified number of cards of a given rarity

count: Integer - number of cards to scouted
rarity: String - rarity of all cards in scout
unit: unit of card to scout

return: List - cards scouted
'''
async def scout_request(count, rarity, unit=None, name=None):
    if count == 0:
        return []

    # Build request url
    request_url = API_URL + "cards/?rarity=" + rarity
    request_url += "&ordering=random"
    request_url += "&is_promo=False"
    request_url += "&is_special=False"

    if unit != None:
        request_url += "&idol_main_unit=" + unit
    elif name != None:
        names = name.split(' ')
        request_url += "&name=" + names[0]
        if len(names) == 2:
            request_url += "%" + "20" + names[1]

    request_url += "&page_size=" + str(count)

    # Get and return response
    response = await aiohttp.get(request_url)
    response_json = await response.text()
    response_obj = json.loads(response_json)

    return response_obj#["results"]

'''
Adjusts a pull of a single rarity by checking if a card should flip to a similar
    one and by duplicating random cards in the scout if there were not enough
    scouted.

scout: Dictionary - dictionary representing the scout. All these cards will have
    the same rarity.
required_count: Integer - the number of cards that need to be scouted

return: List - adjusted list of cards scouted
'''
async def get_adjusted_scout(scout, required_count):
    # Add missing cards to scout by duplicating random cards already present
    current_count = len(scout["results"])

    # Something bad happened, return an empty list
    if (current_count == 0):
        return []

    while (current_count < required_count):
        scout["results"].append(
            scout["results"][random.randint(0, current_count - 1)]
        )
        current_count += 1

    # Traverse scout and roll for flips
    for card_index in range(0, len(scout["results"]) - 1):
        # for each card there is a (1 / total cards) chance that we should dupe
        # the previous card
        roll = random.uniform(0, 1)
        if roll <  1 / scout["count"]:
            scout["results"][card_index] = scout["results"][card_index + 1]

    return scout["results"]

'''
Scouts a specified number of cards

count: Integer - number of cards to scouted
guaranteed_sr: Boolean - whether at least one card in the scout will be an SR
unit: String - unit of cards to scout

return: List - cards scouted
'''
async def scout_cards(count, box, guaranteed_sr=False, unit=None, name=None):
    rarities = []

    if guaranteed_sr:
        for r in range(0, count - 1):
            rarities.append(roll_rarity(box))

        if rarities.count("R") + rarities.count("N") == count - 1:
            rarities.append(roll_rarity(box, True))
        else:
            rarities.append(roll_rarity(box))

    # Case where a normal character is selected
    elif box == "regular" and name != None:
        for r in range(0, count - 1):
            rarities.append("N")

    else:
        for r in range(0, count):
            rarities.append(roll_rarity(box))

    results = []

    for rarity in RATES[box].keys():
        if rarities.count(rarity) > 0:
            scout = await scout_request(
                rarities.count(rarity), rarity, unit, name
            )

            results += await get_adjusted_scout(scout, rarities.count(rarity))

    random.shuffle(results)

    return results

'''
Handles a solo scout

message: Object - message object from user requesting scout
unit: String - name of unit being scouted for
name: String - name of idol being scouted for
'''
async def handle_solo_scout(message, box, unit=None, name=None):
    card = await scout_cards(1, box, False, unit, name)

    # Send error message if no card was returned
    if len(card) == 0:
        await client.send_message(
            message.channel,
            "<@" + message.author.id + "> A transmission error occured."
        )
        return

    card = card[0]
    url = ""

    if card["card_image"] == None:
        url = "http:" + card["card_idolized_image"]
    else:
        url = "http:" + card["card_image"]

    image_path = scout_image_generator.IDOL_IMAGES_PATH
    image_path += posixpath.basename(urllib.parse.urlsplit(url).path)

    await scout_image_generator.download_image_from_url(url, image_path)

    await client.send_file(
        message.channel,
        image_path,
        content="<@" + message.author.id + ">",
        tts=False
    )

'''
Handles a scout with multiple cards

message: Object - message object from user requesting scout
unit: String - name of unit being scouted for
name: String - name of idol being scouted for
'''
async def handle_multiple_scout(message, count, box, unit=None, name=None):
    cards = None

    if (box == "honour"):
        cards = await scout_cards(count, box, True, unit, name)
    else:
        cards = await scout_cards(count, box, False, unit, name)

    circle_image_urls = []

    for card in cards:
        if card["round_card_image"] == None:
            circle_image_urls.append(
                "http:" + card["round_card_idolized_image"]
            )
        else:
            circle_image_urls.append("http:" + card["round_card_image"])

    # Send error message if no cards were scouted
    if len(circle_image_urls) == 0:
        await client.send_message(
            message.channel,
            "<@" + message.author.id + "> A transmission error occured."
        )
        return

    image_path = await scout_image_generator.create_image(
        circle_image_urls,
        2,
        str(time.clock()) + message.author.id + ".png"
    )

    await client.send_file(
        message.channel,
        image_path,
        content="<@" + message.author.id + ">",
        tts=False
    )

    os.remove(image_path)

'''
Handles a scout

message: Object - message object from user requesting scout
scout_command: String - the scout command used ("!scout", "!scout11")
scout_arg: String - optional argument passed to scout
'''
async def handle_scout(message, scout_command, scout_arg=None):
    unit = None
    name = None

    if scout_arg == "muse":
        unit = "µ's"
    elif scout_arg == "aqours":
        unit = "aqours"

    i = 0
    while unit == None and name == None and i < len(IDOL_NAMES):
        curr_name_split = IDOL_NAMES[i].split(' ')

        if len(curr_name_split) == 0:
            continue
        elif len(curr_name_split) == 1:
            if scout_arg == curr_name_split[0].lower():
                name = IDOL_NAMES[i]
        elif scout_arg == curr_name_split[1].lower():
            name = IDOL_NAMES[i]

        i += 1

    if scout_command == "!scout":
        await handle_solo_scout(message, "honour", unit, name)

    elif scout_command == "!scout11":
        await handle_multiple_scout(message, 11, "honour", unit, name)

    elif scout_command == "!scoutregular" or scout_command == "!scoutr":
        await handle_solo_scout(message, "regular", None, name)

    elif scout_command == "!scoutregular10" or scout_command == "!scoutr10":
        await handle_multiple_scout(message, 10, "regular", None, name)

    elif scout_command == "!scoutcoupon" or scout_command == "!scoutc":
        await handle_solo_scout(message, "coupon", unit, name)

    logger.log_request(message, "scout")

'''
Updates rate limiting and checks if a request by a user exceed their rate limit

message: Object - sender's message object

Return: Boolean - True if rate limit exceeded, otherwise false
'''
def rate_limit_check(message):
    INTERVAL = 2.50 # Seconds
    MAX_COUNT = 5

    user_id = message.author.id

    # Add rate limit info for user if it does not exist
    if not user_id in rate_limits.keys():
        rate_limits[user_id] = {"count": 0, "last": time.time()}

    # Decrease count by one for each interval user has not made a request
    curr_time = time.time()
    time_delta = curr_time - rate_limits[user_id]["last"]
    rate_limits[user_id]["count"] -= int(math.floor(time_delta / INTERVAL))

    if rate_limits[user_id]["count"] < 0:
        rate_limits[user_id]["count"] = 0

    # Return true if limit exceeded
    if rate_limits[user_id]["count"] > MAX_COUNT:
        return True

    # Otherwise increase count
    rate_limits[user_id]["count"] += 1
    rate_limits[user_id]["last"] = curr_time

    return False

'''
Runs task that will handle a message

message: message object
'''
async def handle_message(message):
    if message.author.bot:
        return

    command = None
    command_arg = None

    message_split = message.content.split(' ')

    if len(message_split) >= 1:
        command = message_split[0].lower()

    if len(message_split) >= 2:
        command_arg = message_split[1].lower()

    if command != None:
        if command.startswith("!scout"):
            if not rate_limit_check(message):
                await handle_scout(message, command, command_arg)
            else:
                await client.send_message(
                    message.channel,
                    "<@" + message.author.id + "> slow down! Spamming this "
                    + "command slows me down for others."
                )

# The rest of handle scout ...
        elif command.startswith("!info") or command.startswith("!help"):
            reply = "Instructions for how to use the bot can be found here:\n"
            reply += "<https://github.com/DamourYouKnow/"
            reply += "HAHA-NO-UR/blob/master/README.md>\n\n"
            reply += "If you have any suggestions for new feautures or "
            reply += "improvements contact D'Amour#2601 on discord or submit "
            reply += "a request here:\n"
            reply += "<https://github.com/DamourYouKnow/HAHA-NO-UR/issues>\n\n"
            reply += "Feel free to add this bot to your own server or host "
            reply += "your own version of it. If you are interested in "
            reply += "contributing to the bot please contact me. "
            reply += "I'm willing to teach so don't worry about not having any "
            reply += "programming experience."

            await client.send_message(message.channel, reply)

@client.event
async def on_message(message):
    try:
        await handle_message(message)

    except Exception as e:
        err = "<@" + message.author.id + "> A transmission error occured.\n\n"
        err += "`" + str(e) + "`"
        traceback.print_exc()
        client.send_message(message.channel, err)

@client.event
async def on_error(event, *args, **kwargs):
    traceback.print_exc()

@client.event
async def on_ready():
    print("Logged in")
    print(str(len(client.servers)) + " servers detected")

    await client.change_presence(game=discord.Game(name="!info"))

# wrap run_bot in loop that handle exceptions
run_bot()
