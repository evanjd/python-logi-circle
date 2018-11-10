"""Authorization provider for the Logi Circle API wrapper"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import os
import logging
import pickle
from urllib.parse import urlencode
import aiohttp

from .const import AUTH_ENDPOINT, TOKEN_ENDPOINT
from .exception import AuthorizationFailed

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
    def authorize_url(self):
        """Returns the authorization URL for the Logi Circle API"""
        query_string = {"response_type": "code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uri": self.redirect_uri,
                        "scope": self.scopes}

        return '%s?%s' % (AUTH_ENDPOINT, urlencode(query_string))

    async def authorize(self, code):
        """Request a bearer token with the supplied authorization code"""
        authorize_payload = {"grant_type": "authorization_code",
                             "code": code,
                             "redirect_uri": self.redirect_uri,
                             "client_id": self.client_id,
                             "client_secret": self.client_secret}

        session = aiohttp.ClientSession()
        async with session.post(TOKEN_ENDPOINT, data=authorize_payload) as req:
            response = await req.json()

            if req.status >= 400:
                error_message = response.get(
                    "error_description", "Non-OK code %s returned" % (req.status))
                raise AuthorizationFailed(error_message)

            # Authorization succeeded. Persist the refresh and access tokens.
            self.tokens[self.client_id] = response
            self.session = session
            self._save_token()

    @property
    def authorized(self):
        """Checks if the current client ID has a refresh token"""
        return self.client_id in self.tokens and 'refresh_token' in self.tokens[self.client_id]

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
