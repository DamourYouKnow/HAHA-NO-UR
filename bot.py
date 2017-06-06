from discord import Game
from discord.ext.commands import Bot
from websockets.exceptions import ConnectionClosed
from core import get_idol_names
from logger import log_request


class HahaNoUR(Bot):
    def __init__(self, prefix: str):
        """
        Initialize an instance of the bot.

        :param prefix: the bot prefix
        """
        self.idol_names = None
        self.main_units = ["µ's'", 'Aqours']
        self.rates = {
            "regular": {"N": 0.95, "R": 0.05, "SR": 0.00, "SSR": 0.00,
                        "UR": 0.00},
            "honour": {"N": 0.00, "R": 0.80, "SR": 0.15, "SSR": 0.04,
                       "UR": 0.01},
            "coupon": {"N": 0.00, "R": 0.00, "SR": 0.80, "SSR": 0.00,
                       "UR": 0.20}
        }

        super().__init__(prefix)

    async def on_ready(self):
        """
        Event for when the bot is ready.
        """
        self.idol_names = await get_idol_names()
        print("Logged in")
        print(str(len(self.servers)) + " servers detected")

        async def __change_presence():
            try:
                await self.wait_until_ready()
                await self.change_presence(game=Game(name="!info"))

            except ConnectionClosed:
                await self.logout()
                await self.login()
                __change_presence()

        await __change_presence()

    async def process_commands(self, message):
        """
        Overwrites the process_commands method to ignore bot users and
        log commands.
        """
        if message.author.bot:
            return

        await super().process_commands(message)
        log_request(message, 'request')
