import discord
import random
import json
import requests
import asyncio

API_URL = "http://schoolido.lu/api/"

# Constants for scouting rates
R_RATE = 0.80
SR_RATE = 0.15
SSR_RATE = 0.04
UR_RATE = 0.01

client = discord.Client()

'''
Generates a random rarity based on the defined scouting rates

return: String - rarity represented as a string ("UR", "SSR", "SR", "R")
'''
def roll_rarity():
    roll = random.uniform(0, 1)

    if roll < UR_RATE:
        return "UR"
    elif roll < SSR_RATE:
        return "SSR"
    elif roll < SR_RATE:
        return "SR"
    else:
        return "R"

'''
Scouts a single card

return: Dictionary - card scouted
'''
async def scout_card():
        # Build request url
        request_url = API_URL + "cards/?rarity=" + roll_rarity()
        request_url += "&ordering=random"
        request_url += "&is_promo=False"
        request_url += "&is_special=False"
        request_url += "&page_size=1"

        response = requests.get(request_url)
        response_obj = json.loads(response.text)

        return response_obj["results"][0]

'''
Scouts a specified number of cards

return: List - cards scouted
'''
def scout_cards(count):
    rarities = []

'''
Checks if a card belongs to a minor idol unit (Saint Snow, A-RISE)

card: Dictionary - card being checked

return: Boolean - True if minor unit, otherwise False
'''
def is_minor_unit(card):
    unit = card["idol"]["main_unit"]
    return (unit == "A-RISE") or (unit == "Saint Snow")

@client.event
async def on_message(message):
    reply = ""

    if message.content.startswith("!scout"):
        try:
            card = await scout_card()

            # Draw new card if A-RISE member
            while is_minor_unit(card):
                card = await scout_card()

            reply = "<@" + message.author.id + "> "

            if card["card_image"] == None:
                reply += "http:" + card["card_idolized_image"]
            else:
                reply += "http:" + card["card_image"]

        except Exception as e:
            reply = "<@" + message.author.id + "> A transmission error occured."
            print(str(e))

        await client.send_message(message.channel, reply)

@client.event
async def on_ready():
    print("Logged in")

# Get login token from text file and run client
fp_token = open("token.txt", "r")
token = fp_token.read().strip("\n")
client.run(token)
