from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['haha-no-ur']
col = db['users']

user_ids = col.find().distinct('_id')
total = len(user_ids)
i = 1

for user_id in user_ids:
    user = col.find_one({'_id': user_id})
    album = user['album']
    for card in album:
        card.pop('rarity', None)
        card.pop('attribute', None)
        card.pop('release_date', None)
        card.pop('round_card_image', None)
        card.pop('round_card_idolized_image', None)
        card.pop('name', None)
        card.pop('year', None)
        card.pop('main_unit', None)
        card.pop('sub_unit', None)

    col.update({'_id': user_id}, {'$set': {'album': album}})
    print(str(i) + '/' + str(total))
    i += 1

print('done')
