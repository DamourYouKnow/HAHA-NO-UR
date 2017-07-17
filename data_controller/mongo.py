import time

import pymongo
from discord import User

PORT = 27017
DATABASE_NAME = "haha-no-ur"


class DatabaseController:
    """
    Class for providing a controller that performs operations on
        a mongodb database.
    """

    def __init__(self):
        """
        Constructor for a DatabaseController.
        """
        self._client = pymongo.MongoClient("localhost", PORT)
        self._db = self._client[DATABASE_NAME]

    def __del__(self):
        """
        Destructor for a DatabaseContoller.
        """
        # Close the connection to mongodb
        self._client.close()

    def insert_user(self, user: User):
        """
        Insert a new user into the database.

        :param user: User object of new user.
        """
        user_dict = {
            "_id": user.id,
            "album": []
        }

        self._db["users"].insert_one(user_dict)

    def delete_user(self, user: User):
        """
        Delete a user from the database.

        :param user: User object of the user to delete.
        """
        self._db["users"].delete_one({"_id": user.id})

    def find_user(self, user: User) -> dict:
        """
        Finds a user in the database.

        :param user: Object of user to find in the database.

        :return: Dictionary of found user.
        """
        return self._db["users"].find_one({"_id": user.id})

    def get_user_album(self, user: User) -> list:
        """
        Gets the cards album of a user.

        :param user: User object of the user to query the album from.

        :return: Card album list.
        """
        # Query cards in user's album.
        user_doc = self.find_user(user)
        if not user_doc:
            return []
        return user_doc['album']

    def add_to_user_album(self, user: User, new_cards: list,
                          idolized: bool = False):
        """
        Adds a list of cards to a user's card album.

        :param user: User object of the user who's album will be added to.
        :param new_cards: List of dictionaries of new cards to add.
        :param idolized: Whether the new cards being added are idolized.
        """
        for card in new_cards:
            # User does not have this card, push to album
            if not self._user_has_card(user, card["id"]):
                card["unidolized_count"] = 0
                card["idolized_count"] = 0

                card["time_aquired"] = int(round(time.time() * 1000))

                sort = {"id": 1}
                insert_card = {"$each": [card], "$sort": sort}

                self._db["users"].update_one(
                    {"_id": user.id},
                    {"$push": {"album": insert_card}}
                )

            # User has this card, increment count
            else:
                if idolized:
                    self._db["users"].update(
                        {"_id": user.id, "album.id": card["id"]},
                        {"$inc": {"album.$.idolized_count": 1}}
                    )
                else:
                    self._db["users"].update(
                        {"_id": user.id, "album.id": card["id"]},
                        {"$inc": {"album.$.unidolized_count": 1}}
                    )

    def _user_has_card(self, user: User, card_id: int) -> bool:
        search_filter = {"$elemMatch": {"id": card_id}}

        search = self._db["users"].find_one(
            {"_id": user.id},
            {"album": search_filter}
        )

        return len(search.keys()) > 1
