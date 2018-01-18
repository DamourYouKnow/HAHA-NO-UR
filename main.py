'''
A discord bot for scouting in Love Live: School Idol Festival.
'''
from asyncio import get_event_loop
from json import load
from time import time
from threading import Thread

from commands import *
from bot import HahaNoUR, get_session_manager
from bot.logger import setup_logging
from config import config_path
from data_controller.mongo import MongoClient
from logs import log_path
from data_controller.card_updater import update_task


def main():
    start_time = int(time())
    logger = setup_logging(start_time, log_path)
    loop = get_event_loop()
    session_manager = loop.run_until_complete(get_session_manager(logger))

    with config_path.joinpath('config.json').open() as f:
        config = load(f)
    with config_path.joinpath('auth.json').open() as f:
        auth = load(f)

    db = MongoClient() if config.get('mongo', True) else None

    bot = HahaNoUR(
        config['default_prefix'], start_time, int(config['colour'], base=16),
        logger, session_manager, db, auth['error_log'], auth['feedback_log']
    )

    bot.remove_command('help')
    cogs = [
        Scout(bot), 
        Album(bot), 
        Info(bot), 
        Stats(bot), 
        Trivia(bot), 
        Config(bot)
    ]

    card_update_thread = Thread(target=update_task)
    card_update_thread.setDaemon(True)
    card_update_thread.start()

    bot.start_bot(cogs, auth['token'])


if __name__ == '__main__':
    main()
