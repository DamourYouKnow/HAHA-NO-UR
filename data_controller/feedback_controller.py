from datetime import datetime
from data_controller.database_controller import DatabaseController

class FeedbackController(DatabaseController):
    def __init__(self, mongo_client):
        """
        Constructor for a FeebackController.

        :param mongo_client: Mongo client used by this controller.
        """
        super().__init__(mongo_client, 'feedback')

    async def add_feedback(self, user_id, username, message):
        """
        Insert a new feedback into the database.
        """
        feedback = {
            'user_id': user_id,
            'username': username,
            'date': datetime.now(),
            'message': message
        }
        await self._collection.insert_one(feedback)