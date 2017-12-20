class DatabaseController:
    """
    Class for providing a controller that performs operations on
        a mongodb database.
    """

    def __init__(self, mongo_client, collection: str):
        """
        Constructor for a DatabaseController.

        :param mongo_client: Mongo client used by this controller.
        """
        self.mongo_client = mongo_client
        self._collection = mongo_client.db[collection]