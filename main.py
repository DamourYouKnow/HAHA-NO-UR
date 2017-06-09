from json import load
from pathlib import Path

from bot import HahaNoUR
from commands import InfoCommands, ScoutCommands


def main():
    with Path('config/config.json').open() as f:
        config = load(f)
        f.close()
    bot = HahaNoUR(config['default_prefix'])
    bot.remove_command('help')
    cogs = [ScoutCommands(bot), InfoCommands(bot)]
    for cog in cogs:
        bot.add_cog(cog)
    bot.run(config['token'])


if __name__ == '__main__':
    main()
