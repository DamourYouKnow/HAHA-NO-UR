import motor.motor_asyncio
from data_controller.user_controller import UserController
from data_controller.card_controller import CardController
from data_controller.feedback_controller import FeedbackController
from data_controller.server_controller import ServerController

PORT = 27017
DATABASE_NAME = "haha-no-ur"

class MongoClient:
    def __init__(self):
        """
        Constructor for a MongoClient
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient("localhost", PORT)
        self.db = self.client[DATABASE_NAME]
        self.users = UserController(self)
        self.cards = CardController(self)
        self.feedback = FeedbackController(self)
        self.servers = ServerController(self)

    def __del__(self):
        """
        Destructor for a MongoClient.
        """
        # Close the connection to mongodb
        self.client.close()



