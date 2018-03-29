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

    async def get_user_count(self) -> int:
        return await self._collection.find().count()

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

    async def get_user_album(self, user_id: str, expand_info: bool=False) -> list:
        """
        Gets the cards album of a user.

        :param user_id: User ID of the user to query the album from.

        :return: Card album list.
        """
        # Query cards in user's album.
        user_doc = await self.find_user(user_id)
        if not user_doc:
            return []

        album = user_doc['album']
        if expand_info:
            album = await self._merge_card_info(album)
  
        return album

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
            result =  search[0]['album'][0]
            result = await self._merge_card_info([result])
            return result[0]
            
        return None

    async def add_to_user_album(self, user_id: str, new_cards: list,
                                idolized: bool = False):
        """
        Adds a list of cards to a user's card album.

        :param user_id: User ID of the user who's album will be added to.
        :param new_cards: List of dictionaries of new cards to add.
        :param idolized: Whether the new cards being added are idolized.
        """
        for card in new_cards:
            if card['card_image'] == None:
                idolized = True

            # User does not have this card, push to album
            if not await self._user_has_card(user_id, card['_id']):
                uc, ic = 1, 0
                if idolized:
                    uc, ic = 0, 1

                new_card = {
                    'id': card['_id'],
                    'unidolized_count': uc,
                    'idolized_count': ic,
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

    async def _merge_card_info(self, album: list) -> list:
        """
        Merges card information to an album.

        :param album: Album list.
        :param card_infos: Card information to join.

        :return: New list of card dictionaries with merged information.
        """
        card_ids = [card['id'] for card in album]
        card_infos = await self.mongo_client.cards.get_cards(card_ids)

        if len(album) != len(card_infos):
            return []

        for i in range(0, len(album)):
            for key in card_infos[i]:
                if key == 'idol':
                    for idol_key in card_infos[i][key]:
                        album[i][idol_key] = card_infos[i][key][idol_key]
                else:
                    album[i][key] = card_infos[i][key]

        return album