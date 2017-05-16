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

def get_main_unit_card_count_by_rarity(rates, main_units):
    counts = {}

    for unit in main_units:
        counts[unit] = {}

        for rarity in rates.keys():
            request_url = API_URL + "cards/?rarity=" + rarity
            request_url += "&idol_main_unit=" + unit
            request_url += "&page_size=1"

            response = requests.get(request_url)

            counts[unit][rarity] = json.loads(response.text)["count"]

    return counts

def get_idol_card_count_by_rarity(rates, idol_names):
    counts = {}

    for idol in idol_names:
        counts[idol] = {}
        names = idol.split(' ')

        for rarity in rates.keys():
            request_url = API_URL + "cards/?rarity=" + rarity
            request_url += "&name=" + names[0] + "%" + "20" + names[1]
            request_url += "&page_size=1"

            response = requests.get(request_url)

            counts[idol][rarity] = json.loads(response.text)["count"]

    return counts
