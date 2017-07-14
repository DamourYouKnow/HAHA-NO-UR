from asyncio import get_event_loop
from json import load
from time import time

from bot import HahaNoUR, get_session_manager
from bot.logger import setup_logging
from commands import *
from config import config_path
from data_controller.mongo import DatabaseController
from logs import log_path


def main():
    start_time = int(time())
    logger = setup_logging(start_time, log_path)
    loop = get_event_loop()
    session_manager = loop.run_until_complete(get_session_manager(logger))

    with config_path.joinpath('config.json').open() as f:
        config = load(f)
    with config_path.joinpath('auth.json').open() as f:
        auth = load(f)

    db = DatabaseController() if config.get('mongo', True) else None

    bot = HahaNoUR(
        config['default_prefix'], start_time, int(config['colour'], base=16),
        logger, session_manager, db, auth['error_log']
    )

    bot.remove_command('help')
    cogs = [Scout(bot), Album(bot), Info(bot)]

    bot.start_bot(cogs, auth['token'])


if __name__ == '__main__':
    main()
