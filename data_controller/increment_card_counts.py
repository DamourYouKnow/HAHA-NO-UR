from mongo import DatabaseController
from discord import User

db = DatabaseController()
ids = db.get_all_user_ids()

for user_id in ids:
    user = User()
    user.id = user_id
    album = db.get_user_album(user)
    db.add_to_user_album(user, album)
