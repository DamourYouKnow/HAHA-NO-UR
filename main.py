from json import loads
from pathlib import Path

from bot import HahaNoUR
from bot_commands import BotCommands


def main():
    with Path('config/config.json').open() as f:
        config = loads(f)
        f.close()
    bot = HahaNoUR(config['default_prefix'])
    bot.remove_command('help')
    bot.add_cog(BotCommands(bot))
    bot.run(config['token'])


if __name__ == '__main__':
    main()
