from core.get_names import get_idol_names

IDOL_NAMES = get_idol_names()

ALIASES = {
    "name": {
        ("honk",): "Kousaka Honoka",
        ("eri",): "Ayase Eli",
        ("yohane",): "Tsushima Yoshiko",
        ("hana", "pana"): "Koizumi Hanayo",
        ("tomato",): "Nishikino Maki",
        ("zura", "woah", "technology"): "Kunikida Hanamaru",
        ("mike",): "Kurosawa Ruby", # Memes
        ("nell",): "Yazawa Nico"
    },
    "main_unit": {
        ("muse", "μ's", "µ's"): "μ's",
        ("aqours", "aquas", "aquors"): "Aqours",
        ("a-rise", "arise"): "A-RISE",
        ("saint", "snow"): "Saint Snow"
    },
    "sub_unit": {
        ("lily", "white"): "Lily White",
        ("bibi",): "Bibi",
        ("printemps",): "Printemps",
        ("guilty", "kiss"): "Guilty Kiss",
        ("azalea",): "Azalea",
        ("cyaron", "cyaron!", "crayon", "crayon!"): "CYaRon!"
    }
}

def parse_arguments(args: tuple, allow_unsupported_lists: bool=False) -> dict:
    """
    Parse all user arguments

    :param args: Tuple of all arguments
    :param allow_unsupported_lists: Whether parameters that School Idol
        Tomodachi does not allow multiple values off are reduced.

    :return: A list of tuples of (arg_type, arg_value)
    """
    parsed_args = {
        "name": [],
        "main_unit": [],
        "sub_unit": [],
        "year": [],
        "attribute": [],
        "rarity": []
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
        if len(parsed_args["sub_unit"]) > 1:
            parsed_args["sub_unit"] = [parsed_args["sub_unit"][0]]
        if len(parsed_args["attribute"]) > 1:
            parsed_args["attribute"] = [parsed_args["attribute"][0]]
        if len(parsed_args["year"]) > 1:
            parsed_args["year"] = [parsed_args["year"][0]]

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
        name_split = full_name.split(" ")

        # Check if name is exact match
        if arg.title() == name_split[-1]:
            return ("name", full_name)

    # Check for unit and idol names by alias
    for alias_dict in ALIASES:
        search_result = _resolve_alias(arg, ALIASES[alias_dict])
        if search_result:
            return (alias_dict, search_result)

    # Check for years
    if arg in ["first", "second", "third"]:
        return ("year", arg.title())

    # Check for attribute
    if arg in ["cool", "smile", "pure"]:
        return ("attribute", arg.title())

    # Check for rarity
    if arg.upper() in ["N", "R", "SR", "SSR", "UR"]:
        return ("rarity", arg.upper())

    return (None, None)


def _resolve_alias(target: str, alias_dict: dict) -> str:
    """
    Resolves an alias from a given alias dicitonary.

    :param target: Target string being searched for.
    :alias_dict: Alias dicitonary being searched in.

    :return: Alias result if found, otherwise returns an empty string.
    """
    for key in alias_dict:
        if target in key:
            return alias_dict[key]

    return ""
