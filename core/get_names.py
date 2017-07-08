from json import dump, load

from requests import get

from data import data_path

API_URL = 'http://schoolido.lu/api/'


def get_idol_names() -> list:
    """
    Gets a list of every idol name (Last First)

    :return: List of names
    """
    path = data_path.joinpath('names.json')
    try:
        size = (get(API_URL + "idols").json())["count"]
        result_list = get(
            API_URL + "idols/?page_size=" + str(size)).json()["results"]
        name = [res['name'] for res in result_list]
    except:
        with path.open() as f:
            name = load(f)
            f.close()
    else:
        with path.open('w+') as f:
            dump(name, f)
            f.close()
    return name
