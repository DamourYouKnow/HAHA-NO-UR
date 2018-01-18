from data_controller.database_controller import DatabaseController

class ServerController(DatabaseController):
    def __init__(self, mongo_client):
        """
        Constructor for a ServerController.

        :param mongo_client: Mongo client used by this controller.
        """
        super().__init__(mongo_client, 'server')

    async def set_prefix(self, server_id: str, prefix: str):
        doc = {'_id': server_id}
        set_prefix = {'$set': {'command_prefix': prefix}}
        await self._collection.update(doc, set_prefix, upsert=True)

    async def get_prefix(self, server_id: str) -> str:
        server = await self._collection.find_one({'_id': server_id})
        if server and server['command_prefix']:
            return server['command_prefix']
        return '!'
            
