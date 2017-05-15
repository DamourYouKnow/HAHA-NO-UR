import discord
import random
import json
import aiohttp
import requests
import asyncio
import os
import time
import traceback
import threading
import posixpath
import urllib
import scout_image_generator
import idol_info

API_URL = "http://schoolido.lu/api/"

# Constants for scouting rates
R_RATE = 0.80
SR_RATE = 0.15
SSR_RATE = 0.04
UR_RATE = 0.01

IDOL_NAMES =  idol_info.get_idol_names()
MAIN_UNITS = ["µ's'", "aqours"]

client = discord.Client()

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
def roll_rarity(guaranteed_sr = False):
    roll = random.uniform(0, 1)

    if roll < UR_RATE:
        return "UR"
    elif roll < SSR_RATE + UR_RATE:
        return "SSR"
    elif roll < SR_RATE + UR_RATE + SSR_RATE:
        return "SR"
    else:
        if guaranteed_sr:
            return "SR"
        else:
            return "R"

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
        request_url += "&name=" + names[0] + "%" + "20" + names[1]

    request_url += "&page_size=" + str(count)

    response = await aiohttp.get(request_url)
    response_json = await response.text()
    response_obj = json.loads(response_json)

    return response_obj["results"]

'''
Scouts a specified number of cards
count: Integer - number of cards to scouted
guaranteed_sr: Boolean - whether at least one card in the scout will be an SR
unit: String - unit of cards to scout
return: List - cards scouted
'''
async def scout_cards(count, guaranteed_sr=False, unit=None, name=None):
    rarities = []

    if guaranteed_sr:
        for r in range(0, count - 1):
            rarities.append(roll_rarity())

        if rarities.count("R") == count - 1:
            rarities.append(roll_rarity(True))
        else:
            rarities.append(roll_rarity())
    else:
        for r in range(0, count):
            rarities.append(roll_rarity())

    results = []
    results += await scout_request(rarities.count("R"), "R", unit, name)
    results += await scout_request(rarities.count("SR"), "SR", unit, name)
    results += await scout_request(rarities.count("SSR"), "SSR", unit, name)
    results += await scout_request(rarities.count("UR"), "UR", unit, name)

    random.shuffle(results)

    return results

'''
Handles a solo scout

scout_command: String - the scout command used ("!scout", "!scout11")
scout_arg: String - optional argument passed to scout
'''
async def handle_solo_scout(message, unit=None, name=None):
    card = await scout_cards(1, False, unit, name)
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

scout_command: String - the scout command used ("!scout", "!scout11")
scout_arg: String - optional argument passed to scout
'''
async def handle_multiple_scout(message, unit=None, name=None):
    cards = await scout_cards(11, True, unit, name)
    circle_image_urls = []

    for card in cards:
        if card["round_card_image"] == None:
            circle_image_urls.append(
                "http:" + card["round_card_idolized_image"]
            )
        else:
            circle_image_urls.append(
                "http:" + card["round_card_image"]
            )

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

scout_command: String - the scout command used ("!scout", "!scout11")
scout_arg: String - optional argument passed to scout
'''
async def handle_scout(message, scout_command, scout_arg=None):
    unit = None
    name = None

    if scout_arg == "muse":
        unit = "µ's"
    elif scout_arg == "aqours":
        unit == "aqours"

    i = 0
    while unit == None and name == None and i < len(IDOL_NAMES):
        curr_name_split = IDOL_NAMES[i].split(' ')

        if len(curr_name_split) < 2:
            break

        if scout_arg == curr_name_split[1].lower():
            name = IDOL_NAMES[i]
        i += 1

    if scout_command == "!scout":
        await handle_solo_scout(message, unit, name)

    elif scout_command in "!scout11":
        await handle_multiple_scout(message, unit, name)

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
            await handle_scout(message, command, command_arg)

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

# wrap run_bot in loop that handle exceptions
run_bot()
