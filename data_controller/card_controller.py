from mongo import MongoClient, DatabaseController

class CardController(DatabaseController):
    def __init__(self, mongo_client: MongoClient):
        """
        Constructor for a UserController.

        :param mongo_client: Mongo client used by this controller.
        """
        super().__init__(mongo_client, 'cards')

    async def upsert_card(self, card: dict):
        """
        Inserts a card into the card collection if it does not exist.

        :param card: Card dictionary to insert.
        """
        card = copy.deepcopy(card)
        card['_id'] = card['id']
        del card['id']

        doc = {'_id': card['_id']}
        setCard = {'$set': card}

        await self._collection.update(doc, setCard, upsert=True)
