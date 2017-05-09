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

async def roll_rarity():
    roll = random.uniform(0, 1)

    if roll < UR_RATE:
        return "UR"
    elif roll < SSR_RATE:
        return "SSR"
    elif roll < SR_RATE:
        return "SR"
    else:
        return "R"

@client.event
async def on_message(message):
    reply = ""

    if message.content == "!scout":
        rarity = await roll_rarity()

        request_url = API_URL + "cards/?ordering=random&rarity=" + rarity + "&page_size=1"
        response = requests.get(request_url)
        response_obj = json.loads(response.text)
        card = response_obj["results"][0]

        # Post idolized card if promo
        if card["card_image"] == None:
            reply = card["card_idolized_image"]
        else:
            reply = card["card_image"]
            
        await client.send_message(message.channel, "http:" + reply)

@client.event
async def on_ready():
    print("Logged in")

# Get login token from text file
fp_token = open("token.txt", "r")
token = fp_token.read()
print(token)

# Create and run client
client.run(token)
