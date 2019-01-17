"""Authorization provider for the Logi Circle API wrapper"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import os
import logging
import pickle
from urllib.parse import urlencode
import aiohttp

from .const import AUTH_BASE, AUTH_ENDPOINT, TOKEN_ENDPOINT
from .exception import AuthorizationFailed, NotAuthorized

_LOGGER = logging.getLogger(__name__)


class AuthProvider():
    """OAuth2 client for the Logi Circle API"""

    def __init__(self, client_id, client_secret, redirect_uri, scopes, cache_file, logi_base):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.cache_file = cache_file
        self.logi = logi_base
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

        return '%s?%s' % (AUTH_BASE + AUTH_ENDPOINT, urlencode(query_string))

    @property
    def refresh_token(self):
        """The refresh token granted by the Logi Circle API for the current client ID."""
        if not self.authorized:
            return None
        return self.tokens[self.client_id].get('refresh_token')

    @property
    def access_token(self):
        """The access token granted by the Logi Circle API for the current client ID."""
        if not self.authorized:
            return None
        return self.tokens[self.client_id].get('access_token')

    async def authorize(self, code):
        """Request a bearer token with the supplied authorization code"""
        authorize_payload = {"grant_type": "authorization_code",
                             "code": code,
                             "redirect_uri": self.redirect_uri,
                             "client_id": self.client_id,
                             "client_secret": self.client_secret}

        await self._authenticate(authorize_payload)

    async def clear_authorization(self):
        """Logs out and clears all persisted tokens for this client ID."""
        await self.close()

        self.tokens[self.client_id] = {}
        self._save_token()

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

    async def close(self):
        """Closes the aiohttp session."""
        for subscription in self.logi.subscriptions:
            if subscription.opened:
                # Signal subscription to close itself when the next frame is processed.
                subscription.invalidate()
                _LOGGER.warning('One or more WS connections have not been closed.')

        if isinstance(self.session, aiohttp.ClientSession):
            await self.session.close()
            self.session = None
            self.logi.is_connected = False

    async def _authenticate(self, payload):
        """Request or refresh the access token with Logi Circle"""

        session = await self.get_session()
        async with session.post(AUTH_BASE + TOKEN_ENDPOINT, data=payload) as req:
            response = await req.json()

            if req.status >= 400:
                self.logi.is_connected = False
                error_message = response.get(
                    "error_description", "Non-OK code %s returned" % (req.status))
                raise AuthorizationFailed(error_message)

            # Authorization succeeded. Persist the refresh and access tokens.
            self.logi.is_connected = True
            self.tokens[self.client_id] = response
            self._save_token()

    async def get_session(self):
        """Returns a aiohttp session, creating one if it doesn't already exist."""
        if not isinstance(self.session, aiohttp.ClientSession):
            self.session = aiohttp.ClientSession()
            self.logi.is_connected = True

        return self.session

    def _save_token(self):
        """Dump data into a pickle file."""
        with open(self.cache_file, 'wb') as pickle_db:
            pickle.dump(self.tokens, pickle_db)
        return True

    def _read_token(self):
        """Read data from a pickle file."""
        filename = self.cache_file
        if os.path.isfile(filename):
            data = pickle.load(open(filename, 'rb'))
            return data
        return {}
