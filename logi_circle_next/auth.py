"""Authorization provider for the Logi Circle API wrapper"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import os
import logging
import pickle
from urllib.parse import urlencode
import aiohttp

from .const import AUTH_ENDPOINT, TOKEN_ENDPOINT
from .exception import AuthorizationFailed, NotAuthorized

_LOGGER = logging.getLogger(__name__)


class AuthProvider():
    """OAuth2 client for the Logi Circle API"""

    def __init__(self, client_id, client_secret, redirect_uri, scopes, cache_file):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.cache_file = cache_file
        self.tokens = self._read_token()
        self.session = None

    @property
    def authorized(self):
        """Checks if the current client ID has a refresh token"""
        return self.client_id in self.tokens and 'refresh_token' in self.tokens[self.client_id]

    @property
    def authorize_url(self):
        """Returns the authorization URL for the Logi Circle API"""
        query_string = {"response_type": "code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "scope": self.scopes}

        return '%s?%s' % (AUTH_ENDPOINT, urlencode(query_string))

    @property
    def refresh_token(self):
        """The refresh token granted by the Logi Circle API for the current client ID."""
        if not self.authorized:
            return None
        return self.tokens[self.client_id].get('refresh_token')

    async def authorize(self, code):
        """Request a bearer token with the supplied authorization code"""
        authorize_payload = {"grant_type": "authorization_code",
                             "code": code,
                             "redirect_uri": self.redirect_uri,
                             "client_id": self.client_id,
                             "client_secret": self.client_secret}

        await self._authenticate(authorize_payload)

    async def refresh(self):
        """Use the persisted refresh token to request a new access token."""
        if not self.authorized:
            raise NotAuthorized(
                'No refresh token is available for client ID %s' % (self.client_id))

        refresh_payload = {"grant_type": "refresh_token",
                           "refresh_token": self.refresh_token,
                           "client_id": self.client_id,
                           "client_secret": self.client_secret}

        await self._authenticate(refresh_payload)

    async def _authenticate(self, payload):
        """Request or refresh the access token with Logi Circle"""

        await self._create_session()
        async with self.session.post(TOKEN_ENDPOINT, data=payload) as req:
            response = await req.json()

            if req.status >= 400:
                error_message = response.get(
                    "error_description", "Non-OK code %s returned" % (req.status))
                raise AuthorizationFailed(error_message)

            # Authorization succeeded. Persist the refresh and access tokens.
            self.tokens[self.client_id] = response
            self._save_token()

    async def _create_session(self):
        """Creates an aiohttp session, closing any existing active sessions."""
        if isinstance(self.session, aiohttp.ClientSession):
            await self.session.close()

        self.session = aiohttp.ClientSession()

    def _save_token(self):
        """Dump data into a pickle file."""
        with open(self.cache_file, 'wb') as pickle_db:
            pickle.dump(self.tokens, pickle_db)
        return True

    def _read_token(self):
        """Read data from a pickle file."""
        filename = self.cache_file
        try:
            if os.path.isfile(filename):
                data = pickle.load(open(filename, 'rb'))
                return data

        except (OSError, IOError):
            # File doesn't exist, return an empty object
            return {}