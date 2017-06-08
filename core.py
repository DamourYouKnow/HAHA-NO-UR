import requests
import json

API_URL = 'http://schoolido.lu/api/'

def get_idol_names() -> list:
    """
    Gets a list of every idol name (Last First)

    :return: List of names
    """
    count_url = API_URL + 'idols'
    res_url = API_URL + 'idols/?page_size='

    size = json.loads(requests.get(API_URL + "idols").text)["count"]

    names = []
    response_json = requests.get(API_URL + "idols/?page_size=" + str(size)).text
    result_list = json.loads(response_json)["results"]

    return [res['name'] for res in result_list]
