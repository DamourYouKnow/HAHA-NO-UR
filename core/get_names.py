from json import dump, load

from requests import get

from data import data_path


def __local_names(path) -> list:
    """
    Return the local copy of idol names as fallback.
    :param path: the path to the file.
    :return: a list of names.
    """
    with path.open() as f:
        return load(f)


def get_idol_names() -> list:
    """
    Gets a list of every idol name (Last First)

    :return: List of names
    """
    path = data_path.joinpath('names.json')
    url = 'https://schoolido.lu/api/idols'
    size_resp = get(url)
    if size_resp.status_code != 200:
        return __local_names(path)
    size = size_resp.json().get('count', None)
    if not size:
        return __local_names(path)
    params = {'page_size': str(size)}
    names_resp = get(url, params=params)
    if names_resp.status_code != 200:
        return __local_names(path)
    result_list = names_resp.json().get('results', None)
    if not result_list:
        return __local_names(path)
    names = [res['name'] for res in result_list]
    with path.open('w+') as f:
        dump(names, f)
    return names
