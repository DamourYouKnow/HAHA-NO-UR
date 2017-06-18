from re import findall

from discord.embeds import Embed
from yaml import safe_load

from logger import warning


def get_command_collections(bot) -> tuple:
    """
    Return a list and a dict of the bot commands.
    :param bot: the bot.
    :return: A tuple of (list of bot commands, dict of bot commands)
    The list contains tuples of (tuple of command name, command help)
    The dict has cog name as key and list of tuple of name as val
    """
    aliases = []
    command_list = []
    command_dict = {}
    for key, val in bot.commands.items():
        cog_name = val.cog_name
        command_help = val.help
        name = None
        if key.startswith('_'):
            aliases += val.aliases
            name = tuple([n for n in val.aliases if not n.startswith('_')])
        elif str(val) not in aliases and not str(val).startswith('_'):
            name = (str(val),)
        if name:
            command_list.append((name, command_help))
            if cog_name not in command_dict:
                command_dict[cog_name] = []
            command_dict[cog_name].append(name)
    return command_list, command_dict


def general_help_embed(bot, command_dict):
    """
    Build the general help command for the bot.
    :param bot: the bot.
    :param command_dict: a dict of {cog_name: commands in the cog}
    :return: a discrd embed object of the help.
    """
    help_general = Embed(
        colour=0x4286f4, title='Haha-No-UR Help',
        description='Command help. For extended usage please '
                    'use {}help <command>.'.format(bot.prefix))
    help_general.set_footer(
        text='To check command usage, type {}help <command>'.format(
            bot.prefix
        )
    )
    for cog in bot.cogs:
        commands_str = ', '.join(
            ['/'.join(t) for t in command_dict[str(cog)]])
        split = findall('[A-Z][^A-Z]*', str(cog))
        help_general.add_field(
            name=' '.join(split) + ':', value=commands_str, inline=False)
    return help_general


def detailed_help(command_list):
    """
    Build a dict of help messages for the bot.
    :param command_list: a list of (command name, help message)
    :return: a dict of {command name tuple: help embed}
    """
    res = {}
    for cmd_name, help_msg in command_list:
        try:
            help_msg = safe_load(help_msg)
            help_cmd = Embed(colour=0x4286f4, title='/'.join(cmd_name))
            for key, val in help_msg.items():
                help_cmd.add_field(name=key.title(), value=val, inline=False)
        except Exception as e:
            warning(str(e), date=True)
            help_cmd = Embed(
                colour=0x4286f4, title='/'.join(cmd_name), description=help_msg
            )

        res[cmd_name] = help_cmd

    return res


def get_valid_commands(bot):
    """
    Return a list of every valid user command, including aliases.

    :param bot: The bot.

    :return: Command list.
    """
    cmds = []
    for cmd_and_aliases in get_command_collections(bot)[1].values():
        for alias_tuple in cmd_and_aliases:
            for alias in alias_tuple:
                cmds.append(alias)
    return cmds
