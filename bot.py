from discord import Game
from discord.ext.commands import Bot
from websockets.exceptions import ConnectionClosed

from logger import log_request


class HahaNoUR(Bot):
    def __init__(self, prefix: str):
        """
        Initialize an instance of the bot.

        :param prefix: the bot prefix
        """
        super().__init__(prefix)

    async def on_ready(self):
        """
        Event for when the bot is ready.
        """
        print("Logged in")
        print(str(len(self.servers)) + " servers detected")

        async def __change_presence():
            try:
                await self.wait_until_ready()
                await self.change_presence(game=Game(name="NEW !info"))
            except ConnectionClosed:
                await self.logout()
                await self.login()
                await __change_presence()

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
