from logging import WARN

from discord import Embed
from discord.ext.commands import Group
from yaml import YAMLError, safe_load

from core.api import split_camel


def __resolve_alias(cmd):
    return set([cmd.name] + cmd.aliases)


def get_help(bot) -> tuple:
    """
    Return a general Embed onject for help.
    :param bot: the Yasen instance.
    :return: a discord Embed object for general help.
    """
    from bot import __title__ as name
    prefix = bot.prefix
    description = f'For detailed help please use {prefix}help [command_name]'
    embed = Embed(colour=bot.colour, description=description)
    embed.set_author(name=f'{name} Help', icon_url=bot.user.avatar_url)
    cog_cmd = {}
    all_help = {}
    for command in bot.commands.values():
        _name = command.name
        for n in __resolve_alias(command):
            all_help[n] = single_help(bot, command, _name)
        cog_name = ' '.join(split_camel(command.cog_name) + ['Commands'])
        if cog_name not in cog_cmd:
            cog_cmd[cog_name] = []
        cog_cmd[cog_name].append(f'`{_name}`')
        if isinstance(command, Group):
            for sub in command.commands.values():
                _child_name = sub.name
                full_name = f'{_name} {_child_name}'
                all_help[full_name] = single_help(bot, sub, full_name)
                cog_cmd[cog_name].append(full_name)
    for key in sorted(cog_cmd.keys()):
        embed.add_field(
            name=key, value=', '.join(set(cog_cmd[key])), inline=False
        )
    return embed, all_help


def single_help(bot, cmd, cmd_name) -> Embed:
    """
    Generate help embed for a given embed.
    :return: the embed object for the given command.
    """
    doc = cmd.help
    try:
        help_dict = safe_load(doc)
    except (YAMLError, AttributeError) as e:
        bot.logger.log(WARN, str(e))
        return Embed(colour=bot.colour, description=doc)
    else:
        embed = Embed(
            colour=bot.colour, description=help_dict.pop('Description')
        )
        embed.set_author(name=cmd_name, icon_url=bot.user.avatar_url)
        if cmd.aliases:
            embed.add_field(name='Aliases', value=f'`{", ".join(cmd.aliases)}`')
        for key, val in help_dict.items():
            try:
                val = val.format(prefix=bot.prefix)
            except KeyError:
                val = val.replace('{prefix}', bot.prefix)
            embed.add_field(name=key, value=val, inline=False)
        return embed
