import time
from data_controller.database_controller import DatabaseController
import pprint

class UserController(DatabaseController):
    def __init__(self, mongo_client):
        """
        Constructor for a UserController.

        :param mongo_client: Mongo client used by this controller.
        """
        super().__init__(mongo_client, 'users')

    async def insert_user(self, user_id: str):
        """
        Insert a new user into the database.

        :param user_id: ID of new user.
        """
        await self._collection.insert_one({'_id': user_id, 'album': []})

    async def delete_user(self, user_id: str):
        """
        Delete a user from the database.

        :param user_id: ID of the user to delete.
        """
        await self._collection.delete_one({'_id': user_id})

    async def get_all_user_ids(self) -> list:
        """
        Gets a list of all user ids from the database.

        :return: List of all user ids.
        """
        return await self._collection.find().distinct('_id')

    async def find_user(self, user_id: str) -> dict:
        """
        Finds a user in the database.

        :param user_id: ID of user to find in the database.

        :return: Dictionary of found user.
        """
        return await self._collection.find_one({'_id': user_id})

    async def get_user_album(self, user_id: str) -> list:
        """
        Gets the cards album of a user.

        :param user_id: User ID of the user to query the album from.

        :return: Card album list.
        """
        # Query cards in user's album.
        user_doc = await self.find_user(user_id)
        if not user_doc:
            return []
        return user_doc['album']

    async def get_card_from_album(self, user_id: str, card_id: int) -> dict:
        """
        Gets a card from a user's album.

        :param user_id: User ID of the user to query the card from.

        :return: Card dictionary or None if card does not exist.
        """
        search_filter = {"$elemMatch": {"id": card_id}}
        cursor = self._collection.find(
            {"_id": user_id},
            {"album": search_filter}
        )
        search = await cursor.to_list(None)

        if len(search) > 0 and 'album' in search[0]:
            return search[0]['album'][0]
        return None

    async def get_cards(self, user_id: str, 
                        filters: dict = None, 
                        sorts: dict = None,
                        page: int = None) -> list:
        """
        Searchs for matching cards in a user's album.abs

        :param user_id: User ID of album owner.
        :param filters: Search filters to use.
        :param sorts: Sorts to use.
        """
        match = {'$match': {'_id': user_id}}
        unwind_source = {'$unwind': '$album'}
        lookup = {
            '$lookup': {
                'from': 'cards',
                'localField': 'album.id',
                'foreignField': '_id',
                'as': 'cardObjects'
            }
        }
        unwind_results = {'$unwind': '$cardObjects'}
        group = {
            '$group': {
                '_id': '$_id',
                'cards': {'$push': '$cards'},
                'cardObjects': {'$push': '$cardObjects'}
            } 
        }

        pipeline = [match, unwind_source, lookup, unwind_results, group]
        cursor = self._collection.aggregate(pipeline)
        results = await cursor.to_list(None)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(results)
        raise NotImplementedError

    async def add_to_user_album(self, user_id: str, new_cards: list,
                                idolized: bool = False):
        """
        Adds a list of cards to a user's card album.

        :param user_id: User ID of the user who's album will be added to.
        :param new_cards: List of dictionaries of new cards to add.
        :param idolized: Whether the new cards being added are idolized.
        """
        for card in new_cards:
            # User does not have this card, push to album
            if not await self._user_has_card(user_id, card['_id']):
                new_card = {
                    'id': card['_id'],
                    'unidolized_count': 1,
                    'idolized_count': 0,
                    'time_aquired': int(round(time.time() * 1000))
                }

                sort = {'id': 1}
                insert_card = {'$each': [new_card], '$sort': sort}

                await self._collection.update_one(
                    {'_id': user_id},
                    {'$push': {'album': insert_card}}
                )

            # User has this card, increment count
            else:
                if idolized:
                    await self._collection.update(
                        {'_id': user_id, 'album.id': card['_id']},
                        {'$inc': {'album.$.idolized_count': 1}}
                    )
                else:
                    await self._collection.update(
                        {'_id': user_id, 'album.id': card['_id']},
                        {'$inc': {'album.$.unidolized_count': 1}}
                    )

    async def remove_from_user_album(self, user_id: str, card_id: int,
                                     idolized: bool=False,
                                     count: int=1) -> bool:
        """
        Adds a list of cards to a user's card album.

        :param user: User ID of the user who's album will be added to.
        :param new_cards: List of dictionaries of new cards to add.
        :param idolized: Whether the new cards being added are idolized.

        :return: True if a card was deleted successfully, otherwise False.
        """
        card = await self.get_card_from_album(user_id, card_id)
        if not card:
            return False

        # Get new counts.
        new_unidolized_count = card['unidolized_count']
        new_idolized_count = card['idolized_count']
        if idolized:
            new_idolized_count -= count
        else:
            new_unidolized_count -= count

        # Update values
        await self._collection.update(
            {'_id': user_id, 'album.id': card_id},
            {
                '$set': {
                    'album.$.unidolized_count': new_unidolized_count,
                    'album.$.idolized_count': new_idolized_count
                }
            }
        )
        return True

    async def _user_has_card(self, user_id: str, card_id: int) -> bool:
        search_filter = {'$elemMatch': {'id': card_id}}

        search = await self._collection.find_one(
            {'_id': user_id},
            {'album': search_filter}
        )

        return len(search.keys()) > 1