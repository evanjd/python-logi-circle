"""Python wrapper for the official Logi Circle API"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import sys
import logging
import json
from urllib.parse import urlencode
import aiohttp

from .const import DEFAULT_SCOPES, DEFAULT_CACHE_FILE, API_BASE
from .auth import AuthProvider

_LOGGER = logging.getLogger(__name__)


class LogiCircle():
    """A Python abstraction object to Logi Circle cameras."""

    def __init__(self, client_id, client_secret, redirect_uri, scopes=DEFAULT_SCOPES, cache_file=DEFAULT_CACHE_FILE):
        self.authorization_required = True
        self.is_connected = False
        self.auth_provider = AuthProvider(client_id=client_id,
                                          client_secret=client_secret,
                                          redirect_uri=redirect_uri,
                                          scopes=scopes,
                                          cache_file=cache_file)

        self.authorize_url = self.auth_provider.authorize_url
        self.authorize = self.auth_provider.authorize
