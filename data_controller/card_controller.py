import copy
from data_controller.database_controller import DatabaseController

class CardController(DatabaseController):
    def __init__(self, mongo_client):
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

    async def get_card(self, card_id: int) -> dict:
        """
        Gets a single card from the database.

        :param card_id: ID of card to get.

        :return: Matching card.
        """
        cards = await self.get_cards([card_id])
        if cards:
            return cards[0]
        return None

    async def get_cards(self, card_ids: list) -> list:
        """
        Gets a list of cards from the database.

        :param card_ids: List of card IDs to get.

        :return: Matching cards.
        """
        search = {'_id': {'$in': card_ids}}
        show = {
            'idol.name': 1,
            'idol.year': 1,
            'idol.main_unit': 1,
            'idol.sub_unit': 1,
            'rarity': 1,
            'attribute': 1,
            'card_image': 1,
            'release_date': 1,
            'card_idolized_image': 1,
            'round_card_image': 1,
            'round_card_idolized_image': 1
        }
        cursor = self._collection.find(search, show)
        return await cursor.to_list(None)

    async def get_random_cards(self, filters: dict, count: int) -> list:
        """
        Gets a random list of cards.

        :param filters: Dicitonary of filters to use.
        :param count: Number of results to return.

        :return: Random list of cards.
        """
        match = {'$match': filters}
        sample = {'$sample': {'size': count}}
        cursor = self._collection.aggregate([match, sample])
        return await cursor.to_list(None)

    async def get_card_ids(self) -> list:
        """
        Gets a list of all card IDs in the datase.

        :return: List of card IDs.
        """
        return await self._collection.distinct('_id')

    async def get_idol_names(self) -> list:
        return await self._collection.distinct('idol.name')
