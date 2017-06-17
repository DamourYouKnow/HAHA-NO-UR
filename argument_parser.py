from get_names import get_idol_names

IDOL_NAMES = get_idol_names()

ALIASES = {
    "names": {
        ("honk",): "kousaka honoka",
        ("eri",): "ayase eli",
        ("yohane",): "tsushima yoshiko",
        ("hana", "pana"): "koizumi hanayo",
        ("tomato",): "nishikino maki"
    },
    "main_units": {
        ("muse", "µ's"): "µ's",
        ("aqours", "aquas", "aquors"): "aqours",
        ("a-rise", "arise"): "a-rise",
        ("saint", "snow"): "saint snow"
    },
    "sub_units": {
        ("lily", "white"): "lily white",
        ("bibi",): "bibi",
        ("printemps",): "printemps",
        ("guilty", "kiss"): "guilty kiss",
        ("azalea",): "azalea",
        ("cyaron", "cyaron!", "crayon", "crayon!"): "cyaron!"
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
        "names": [],
        "main_units": [],
        "sub_units": [],
        "years": [],
        "attributes": [],
        "rarities": [],
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
        if len(parsed_args["sub_units"]) > 1:
            parsed_args["sub_units"] = [parsed_args["sub_units"][0]]
        if len(parsed_args["attributes"]) > 1:
            parsed_args["attributes"] = [parsed_args["attributes"][0]]
        if len(parsed_args["years"]) > 1:
            parsed_args["years"] = [parsed_args["years"][0]]

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
            return ("names", full_name)

    # Check for unit and idol names by alias
    for alias_dict in ALIASES:
        search_result = _resolve_alias(arg, ALIASES[alias_dict])
        if search_result:
            return (alias_dict, search_result)

    # Check for years
    if arg in ["first", "second", "third"]:
        return ("years", arg)

    # Check for attribute
    if arg in ["cool", "smile", "pure"]:
        return ("attributes", arg.title())

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
