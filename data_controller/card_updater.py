import discord
import asyncio

async def update_task(bot):
    await bot.wait_until_ready()
    while not bot.is_closed:

        await asyncio.sleep(30)
