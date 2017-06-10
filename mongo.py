import pymongo

PORT = "27017"
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
        self._db = _client[DATABASE_NAME]

    def __del__(self):
        """
        Destructor for a DatabaseContoller.
        """
        # Close the connection to mongodb
        self._client.disconnect()

    def insert_user(self, user: User)
        """
        Insert a new user into the database.

        :param user: User object of new user.
        """
        user_dict = {
            "user_id": user,
            "album": {}
            # TODO, figure out what else we want to save about a user
        }

        self._insert_document(user_dict)

    def delete_user(self, user: User):
        """
        Delete a user from the database.

        :param user: User object of the user to delete.
        """
        self._delete_by_field("users", "user_id", user.id)

    def get_user_album(self, user: User, sort_by: str="card_id") -> dict:
        """
        Gets the cards album of a user.

        :param user: User object of the user to query the album from.
        :param sort_by: How the album will be sorted (defaults to card_id).

        :return: Sorted card album dictionary.
        """
        print("Not implemented")

    def add_to_user_album(self, user: User, new_cards: list,
            idolized: bool=False):
        """
        Adds a list of cards to a user's card album.

        :param user: User object of the user who's album will be added to.
        :param new_cards: List of dictionaries of new cards to add.
        :param idolized: Whether the new cards being added are idolized.
        """
        print("Not implemented")

    def find_user(self, user: User) -> dict:
        """
        Finds a user in the database.

        :param user: Object of user to find in the database.

        :return: Dictionary of found user.
        """
        print("Not implemented")

    def _insert_document(self, collection: str, document: dict):
        self._db[collection].insert_one(document)


    def _update_document(self, collection: str document: dict):
        print("Not implemented")

    def _delete_by_field(self, collection: str, field_name: str, value: str):
        self._db[collection].delete_one({field_name: value})
