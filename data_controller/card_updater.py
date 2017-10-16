import asyncio
import logging

MAX_UPDATE_SIZE = 15

async def update_task(bot):
    await bot.wait_until_ready()
    while not bot.is_closed:
        bot.logger.log(logging.INFO, 'Updating cards list')

        # Get card ids from database and api.
        db_card_ids = set(await bot.db.cards.get_card_ids())
        api_card_ids = set(await bot.session_manager.get_json(
                'http://schoolido.lu/api/cardids'))
        new_card_ids = list(api_card_ids - db_card_ids)

        if len(new_card_ids) > 0:
            new_card_ids = new_card_ids[:MAX_UPDATE_SIZE]

            res = await bot.session_manager.get_json(
                    'http://schoolido.lu/api/cards',
                    {'ids': ','.join(str(i) for i in new_card_ids)})

            for card in res['results']:
                if validate_card(card):
                    await bot.db.cards.upsert_card(card)

        await asyncio.sleep(120)


def validate_card(card: dict) -> bool:
    if not card['card_image'] and not card['card_idolized_image']:
        return False
    if not card['round_card_image'] and not card['round_card_idolized_image']:
        return False
    return True
