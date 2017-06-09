import pymongo

PORT = "27017"

def insert_user(user: User)
    user_dict = {
        "user_id": user,
        "album": {}
        # TODO, figure out what else we want to save about a user
    }

    _insert_document(user_dict)
    

def delete_user(user: User):
    _delete_by_field("users", "user_id", user.id)


def get_user_album(user: User):
    print("Not implemented")


def add_to_user_album(user: User, list: dict, idolized: bool=False):
    print("Not implemented")


def find_user(user: User):
    print("Not implemented")


def _insert_document(collection: str, document: dict):
    # TODO Connection logic
    db[collection].insert_one(document)


def _update_document(collection: str document: dict):
    print("Not implemented")


def _delete_by_field(collection: str, field_name: str, value: str):
    # TODO Connection logic
    db[collection].delete_one({field_name: value})
