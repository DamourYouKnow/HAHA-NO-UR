import requests
import json

API_URL = "http://schoolido.lu/api/"

def get_idol_names():
    size = json.loads(requests.get(API_URL + "idols").text)["count"]

    names = []
    response_json = requests.get(API_URL + "idols/?page_size=" + str(size)).text
    result_list = json.loads(response_json)["results"]

    for result in result_list:
        names.append(result["name"])

    return names
