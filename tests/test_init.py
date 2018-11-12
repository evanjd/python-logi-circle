# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import json
from urllib.parse import urlparse, parse_qs
import pickle
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import AUTH_HOST, TOKEN_ENDPOINT, DEFAULT_SCOPES
from logi_circle.exception import NotAuthorized, AuthorizationFailed
from logi_circle.auth import AuthProvider


class TestAuth(LogiUnitTestBase):
    """Unit test for core Logi class."""

    def test_fetch_no_auth(self):
        """Fetch should return NotAuthorized if no access token is present"""
        logi = self.logi

        async def run_test():
            with self.assertRaises(NotAuthorized):
                await logi._fetch(url='/api')
