from http import HTTPStatus
from json import loads

from aiohttp import ClientResponse, ClientSession
from discord.ext.commands import CommandError
import logging


class HTTPStatusError(CommandError):
    def __init__(self, code: int, msg: str, url: str):
        self.code = code
        self.msg = msg
        self.url = url

    def __str__(self):
        return (f'HTTPStatusError:'
                f'\nUrl: {self.url}\nCode: {self.code}\nMessage: {self.msg}')


async def get_session_manager(logger):
    """
    Get an instance of SessionManager.
    :param logger: the logger used.
    :return: the instance of SessionManager.
    """
    session = ClientSession()
    return SessionManager(session, logger)


class SessionManager:
    """
    An aiohttp client session manager.
    """

    def __init__(self, session: ClientSession, logger):
        """
        Initialize the instance of this class.
        """
        self.session = session
        self.logger = logger
        self.codes = {
            val.value: key
            for key, val in HTTPStatus.__members__.items()
        }

    def __del__(self):
        """
        Class destructor, close the client session.
        """
        self.session.close()

    def get_msg(self, code: int):
        """
        Get the message from an HTTP status code.
        :param code: the status code.
        :return: the message.
        """
        try:
            return self.codes[code]
        except KeyError:
            return None

    def return_response(self, res, code, url):
        """
        Return an Aiohttp or Request response object.
        :param res: the response.
        :param code: the response code.
        :param url: the request url.
        :return: the response object.
        :raises: HTTPStatusError if status code isn't 200
        """
        if 200 <= code < 300:
            return res
        raise HTTPStatusError(code, self.get_msg(code), url)

    async def get_json(self, url: str, params: dict = None):
        """
        Get the json content from an HTTP request.
        :param url: the url.
        :param params: the request params.
        :return: the json content in a dict if success, else the error message.
        :raises HTTPStatusError: if the status code isn't in the 200s
        """
        res = await self.get(url, params=params)
        async with res:
            text = await res.read()
            return loads(text) if text else None

    async def get(
            self, url, *, allow_redirects=True, **kwargs) -> ClientResponse:
        """
        Make HTTP GET request
        :param url: Request URL, str or URL
        :param allow_redirects: If set to False, do not follow redirects.
        True by default (optional).
        :param kwargs: In order to modify inner request parameters,
        provide kwargs.
        :return: a client response object.
        :raises: HTTPStatusError if status code isn't 200
        """
        query_url = url
        if 'params' in kwargs:
            query_url += get_query_string(kwargs['params'])

        self.logger.log(logging.INFO, 'Sending GET request to ' + query_url)

        r = await self.session.get(
            url, allow_redirects=allow_redirects, **kwargs)
        return self.return_response(r, r.status, url)


def get_query_string(params) -> str:
    """
    Gets the query string of a URL parameter dictionary.abs
    :param params: URL params.
    :return: Query string.
    """
    if not params:
        return ''

    return '?' + '&'.join([str(k) + '=' + str(v) for k, v in params.items()])
