from asyncio import get_event_loop, set_event_loop_policy
from json import load
from pathlib import Path
from time import time

from uvloop import EventLoopPolicy

from bot import HahaNoUR, get_session_manager
from bot.logger import setup_logging
from commands import AlbumCommands, InfoCommands, ScoutCommands
from data_controller.mongo import DatabaseController


def main():
    start_time = int(time())
    log_path = Path(Path(__file__).parent.joinpath('logs'))
    logger = setup_logging(start_time, log_path)
    set_event_loop_policy(EventLoopPolicy())
    loop = get_event_loop()
    session_manager = loop.run_until_complete(get_session_manager(logger))
    db = DatabaseController()
    with Path('config/config.json').open() as f:
        config = load(f)
        f.close()
    bot = HahaNoUR(config['default_prefix'], start_time, logger,
                   session_manager, db, config['error_log'])
    bot.remove_command('help')
    cogs = [ScoutCommands(bot), AlbumCommands(bot), InfoCommands(bot)]
    bot.start_bot(cogs, config['token'])


if __name__ == '__main__':
    main()
