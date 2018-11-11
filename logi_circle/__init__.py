"""Python wrapper for the official Logi Circle API"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging

from .const import DEFAULT_SCOPES, DEFAULT_CACHE_FILE
from .auth import AuthProvider

_LOGGER = logging.getLogger(__name__)


class LogiCircle():
    """A Python abstraction object to Logi Circle cameras."""

    def __init__(self, client_id, client_secret, redirect_uri, scopes=DEFAULT_SCOPES, cache_file=DEFAULT_CACHE_FILE):
        self.auth_provider = AuthProvider(client_id=client_id,
                                          client_secret=client_secret,
                                          redirect_uri=redirect_uri,
                                          scopes=scopes,
                                          cache_file=cache_file,
                                          logi_base=self)
        self.authorize = self.auth_provider.authorize
        self.is_connected = False

    @property
    def authorized(self):
        """Checks if the current client ID has a refresh token"""
        return self.auth_provider.authorized

    @property
    def authorize_url(self):
        """Returns the authorization URL for the Logi Circle API"""
        return self.auth_provider.authorize_url
