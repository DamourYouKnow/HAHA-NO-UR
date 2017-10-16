from core.get_names import get_idol_names

IDOL_NAMES = get_idol_names()

ALIASES = {
    'name': {
        'honk': 'Kousaka Honoka',
        'bird': 'Minami Kotori',
        'birb': 'Minami Kotori',
        'eri': 'Ayase Eli',
        'yohane': 'Tsushima Yoshiko',
        'hana': 'Koizumi Hanayo',
        'pana': 'Koizumi Hanayo',
        'tomato': "Nishikino Maki",
        'zura': 'Kunikida Hanamaru',
        'technology': 'Kunikida Hanamaru',
        'woah': 'Kunikida Hanamaru',
        'mike': 'Kurosawa Ruby',  # Memes
        'nell': "Yazawa Nico"
    },
    'main_unit': {
        'muse': "μ's",
        "μ's": "μ's",
        "µ's": "μ's",
        'aqours': 'Aqours',
        'aquas': 'Aqours',
        'aquors': 'Aqours',
        'a-rise': 'A-RISE',
        'arise': 'A-RISE',
        'saint': 'Saint Snow',
        'snow': 'Saint Snow'
    },
    'sub_unit': {
        'lily': 'Lily White',
        'white': 'Lily White',
        'bibi': 'Bibi',
        'printemps': 'Printemps',
        'guilty': 'Guilty Kiss',
        'kiss': 'Guilty Kiss',
        'azalea': 'AZALEA',
        'cyaron': 'CYaRon!',
        'cyaron!': 'CYaRon!',
        'crayon': 'CYaRon!',
        'crayon!': 'CYaRon!'
    }
}


def parse_arguments(args: tuple, allow_unsupported_lists: bool = False) -> dict:
    """
    Parse all user arguments

    :param args: Tuple of all arguments
    :param allow_unsupported_lists: Whether parameters that School Idol
        Tomodachi does not allow multiple values off are reduced.

    :return: A list of tuples of (arg_type, arg_value)
    """
    parsed_args = {
        'name': [],
        'main_unit': [],
        'sub_unit': [],
        'year': [],
        'attribute': [],
        'rarity': []
    }

    for arg in args:
        arg_type, arg_value = _parse_argument(arg)
        if arg_type:
            parsed_args[arg_type].append(arg_value)

    # Covert all values to sets and back to lists to remove duplicates.
    for arg_type in parsed_args:
        parsed_args[arg_type] = list(set(parsed_args[arg_type]))

    # Remove mutiple values from fields not supported
    if not allow_unsupported_lists:
        for key in ('sub_unit', 'attribute', 'year'):
            parsed_args[key] = parsed_args[key][:1]
    return parsed_args


def _parse_argument(arg: str) -> tuple:
    """
    Parse user argument.

    :param arg: An argument.

    :return: Tuple of (arg_type, arg_value)
    """
    arg = arg.lower()

    # Check for names
    for full_name in IDOL_NAMES:
        name_split = full_name.split(' ')

        # Check if name is exact match
        if arg.title() == name_split[-1]:
            return 'name', full_name

    # Check for unit and idol names by alias
    for key, val in ALIASES.items():
        search_result = val.get(arg, None)
        if search_result:
            return key, search_result

    # Check for years
    if arg in ('first', 'second', 'third'):
        return 'year', arg.title()

    # Check for attribute
    if arg in ('cool', 'smile', 'pure'):
        return 'attribute', arg.title()

    # Check for rarity
    if arg.upper() in ('N', 'R', 'SR', 'SSR', 'UR'):
        return 'rarity', arg.upper()

    return None, None
