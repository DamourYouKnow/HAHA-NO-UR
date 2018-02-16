import json
import requests
import time
import copy
from pymongo import MongoClient

MAX_UPDATE_SIZE = 15

# This is ugly until I find time for a better solution...
def update_task():
    while True:
        print('Getting cards...')
        client = None
        try:
            client = MongoClient('localhost', 27017)
            db = client['haha-no-ur']

             # Get card ids from database and api.
            db_card_ids = set(get_card_ids(db))
            api_card_ids = set(json.loads(
                    requests.get('http://schoolido.lu/api/cardids').text)) 
            new_card_ids = list(api_card_ids - db_card_ids)
            if len(new_card_ids) > 0:
                new_card_ids = new_card_ids[:MAX_UPDATE_SIZE]
                print('Getting cards ' + str(new_card_ids))
                req = requests.get(
                        url='https://schoolido.lu/api/cards',
                        params={'ids': ','.join(str(i) for i in new_card_ids)})
                res = json.loads(req.text)

                for card in res['results']:
                    if validate_card(card):
                        upsert_card(db, card)

     
        except Exception as e:
            print(e)

        finally:
            client.close()
            time.sleep(120)


def get_card_ids(db) -> list:
    """
    Gets a list of all card IDs in the datase.

    :return: List of card IDs.
    """
    return db['cards'].distinct('_id')

def upsert_card(db, card: dict):
    """
    Inserts a card into the card collection if it does not exist.

    :param card: Card dictionary to insert.
    """
    card = copy.deepcopy(card)
    card['_id'] = card['id']
    del card['id']

    doc = {'_id': card['_id']}
    setCard = {'$set': card}

    db['cards'].update(doc, setCard, upsert=True)


def validate_card(card: dict) -> bool:
    if not card['card_image'] and not card['card_idolized_image']:
        return False
    if not card['round_card_image'] and not card['round_card_idolized_image']:
        return False
    return True
