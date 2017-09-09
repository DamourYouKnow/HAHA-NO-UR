import discord
import asyncio

async def update_task(bot):
    await bot.wait_until_ready()
    while not bot.is_closed:
        await bot.db.cards.get_card_ids()
        await asyncio.sleep(30)
