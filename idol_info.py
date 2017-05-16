import requests
import json

API_URL = "http://schoolido.lu/api/"

def get_idol_names():
    names = []
    response_json = requests.get(API_URL + "idols/?page_size=18").text
    result_list = json.loads(response_json)["results"]

    for result in result_list:
        names.append(result["name"])

    return names
