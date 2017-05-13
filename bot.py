import discord
import random
import json
import requests
import asyncio
import os
import time
import traceback
import threading
import posixpath
import urllib
import scout_image_generator

API_URL = "http://schoolido.lu/api/"

# Constants for scouting rates
R_RATE = 0.80
SR_RATE = 0.15
SSR_RATE = 0.04
UR_RATE = 0.01

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
def scout_by_rarity(count, rarity, unit = None):
    if count == 0:
        return []

    # Build request url
    request_url = API_URL + "cards/?rarity=" + rarity
    request_url += "&ordering=random"
    request_url += "&is_promo=False"
    request_url += "&is_special=False"

    if unit != None:
        request_url += "&idol_main_unit=" + unit

    request_url += "&page_size=" + str(count)

    response = requests.get(request_url)
    response_obj = json.loads(response.text)

    return response_obj["results"]

'''
Scouts a specified number of cards

count: Integer - number of cards to scouted
guaranteed_sr: Boolean - whether at least one card in the scout will be an SR
unit: String - unit of cards to scout

return: List - cards scouted
'''
def scout_cards(count, guaranteed_sr = False, unit = None):
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
    results += scout_by_rarity(rarities.count("R"), "R", unit)
    results += scout_by_rarity(rarities.count("SR"), "SR", unit)
    results += scout_by_rarity(rarities.count("SSR"), "SSR", unit)
    results += scout_by_rarity(rarities.count("UR"), "UR", unit)
    random.shuffle(results)

    return results

'''
Runs task that will handle a message

message: message object
'''
async def handle_message_task(message):
    reply = ""
    # TODO: delegate some of this stuff to functions
    if message.content.startswith("!scout11 aqours"):
        cards = scout_cards(11, True, "aqours")
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

        image_path = scout_image_generator.create_image(
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

    elif message.content.startswith("!scout11 muse"):
        cards = scout_cards(11, True, "µ's")
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

        image_path = scout_image_generator.create_image(
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

    elif message.content.startswith("!scout11"):
        cards = scout_cards(11, True)
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

        image_path = scout_image_generator.create_image(
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

    elif message.content.startswith("!scout aqours"):
        card = scout_cards(1, False, "aqours")[0]
        url = ""
        reply = "<@" + message.author.id + "> "

        if card["card_image"] == None:
            url = "http:" + card["card_idolized_image"]
        else:
            url = "http:" + card["card_image"]

        image_path = scout_image_generator.IDOL_IMAGES_PATH
        image_path += posixpath.basename(urllib.parse.urlsplit(url).path)

        scout_image_generator.download_image_from_url(url, image_path)

        await client.send_file(
            message.channel,
            image_path,
            content="<@" + message.author.id + ">",
            tts=False
        )

    elif message.content.startswith("!scout muse"):
        card = scout_cards(1, False, "µ's")[0]
        url = ""
        reply = "<@" + message.author.id + "> "

        if card["card_image"] == None:
            url = "http:" + card["card_idolized_image"]
        else:
            url = "http:" + card["card_image"]

        image_path = scout_image_generator.IDOL_IMAGES_PATH
        image_path += posixpath.basename(urllib.parse.urlsplit(url).path)

        scout_image_generator.download_image_from_url(url, image_path)

        await client.send_file(
            message.channel,
            image_path,
            content="<@" + message.author.id + ">",
            tts=False
        )

    elif message.content.startswith("!scout"):
        card = scout_cards(1)[0]
        url = ""
        reply = "<@" + message.author.id + "> "

        if card["card_image"] == None:
            url = "http:" + card["card_idolized_image"]
        else:
            url = "http:" + card["card_image"]

        image_path = scout_image_generator.IDOL_IMAGES_PATH
        image_path += posixpath.basename(urllib.parse.urlsplit(url).path)

        scout_image_generator.download_image_from_url(url, image_path)

        await client.send_file(
            message.channel,
            image_path,
            content="<@" + message.author.id + ">",
            tts=False
        )

@client.event
async def on_message(message):
    try:
        client.loop.create_task(handle_message_task(message))

    except Exception as e:
        err = "<@" + message.author.id + "> A transmission error occured.\n\n"
        err += "`" + str(e) + "`"
        traceback.print_exc()
        client.send_message(message.channel, err)

'''
@client.event
async def on_error(event, *args, **kwargs):
    traceback.print_exc()
    time.sleep(5)
    run_bot()
'''

@client.event
async def on_ready():
    print("Logged in")

# wrap run_bot in loop that handle exceptions
while True:
    try:
        run_bot()
    except:
        print("critical error")
        traceback.print_exc()
        client.close()
        #time.sleep(5)
        #client = discord.Client()

    print("relaunching")
