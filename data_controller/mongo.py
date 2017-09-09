import time
import motor.motor_asyncio
import copy

PORT = 27017
DATABASE_NAME = "haha-no-ur"

class MongoClient:
    def __init__(self):
        """
        Constructor for a MongoClient
        """
        self.users = UserController(self)
        self.cards = CardController(self)
        self.client = motor.motor_asyncio.AsyncIOMotorClient("localhost", PORT)
        self.db = self._client[DATABASE_NAME]

    def __del__(self):
        """
        Destructor for a MongoClient.
        """
        # Close the connection to mongodb
        self.client.close()

class DatabaseController:
    """
    Class for providing a controller that performs operations on
        a mongodb database.
    """

    def __init__(self, mongo_client: MongoClient, collection: str):
        """
        Constructor for a DatabaseController.

        :param mongo_client: Mongo client used by this controller.
        """
        self._collection = mongo_client.db[collection]
