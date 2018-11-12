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

    def test_prelogin_state(self):
        """Validate pre-auth state."""
        logi = self.logi

        async def run_test():
            # Should start false, no login performed yet.
            self.assertFalse(logi.is_connected)
            # No refresh or access token
            self.assertIsNone(logi.auth_provider.refresh_token)
            self.assertIsNone(logi.auth_provider.access_token)
            # Impossible to refresh since there's no refresh token
            with self.assertRaises(NotAuthorized):
                await logi.auth_provider.refresh()

        self.loop.run_until_complete(run_test())

    def test_authorize_url(self):
        """Test authorize URL generation."""
        parsed_url = urlparse(self.logi.authorize_url)
        parsed_qs = parse_qs(parsed_url.query)
        self.assertEqual(parsed_qs['response_type'][0], 'code')
        self.assertEqual(parsed_qs['client_id'][0], self.client_id)
        self.assertEqual(parsed_qs['client_secret'][0], self.client_secret)
        self.assertEqual(parsed_qs['redirect_uri'][0], self.redirect_uri)
        self.assertEqual(parsed_qs['scope'][0], DEFAULT_SCOPES)

    def test_authorize(self):
        """Test successful authorization code and refresh token request handling."""
        logi = self.logi
        auth_fixture = self.fixtures['auth_code']
        dict_auth_fixture = json.loads(auth_fixture)
        refresh_fixture = self.fixtures['refresh_token']
        dict_refresh_fixture = json.loads(refresh_fixture)

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(AUTH_HOST, TOKEN_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=auth_fixture,
                                              headers={'content-type': 'application/json'}))
                arsps.add(AUTH_HOST, TOKEN_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=refresh_fixture,
                                              headers={'content-type': 'application/json'}))
                # Mock authorization, and verify AuthProvider state
                await logi.authorize('beepboop123')
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after successful login')
                self.assertTrue(
                    logi.authorized, 'API reports not authorized after successful login')
                self.assertIsNotNone(
                    logi.auth_provider.session, 'Session not created after successful login')
                self.assertEqual(logi.auth_provider.refresh_token,
                                 dict_auth_fixture['refresh_token'])
                self.assertEqual(logi.auth_provider.access_token,
                                 dict_auth_fixture['access_token'])
                # Mock refresh of access token, and verify AuthProvider state
                await logi.auth_provider.refresh()
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after token refresh')
                self.assertTrue(
                    logi.authorized, 'API reports not authorized after token_refresh')
                self.assertIsNotNone(
                    logi.auth_provider.session, 'Session not created after token_refresh')
                self.assertEqual(logi.auth_provider.refresh_token,
                                 dict_refresh_fixture['refresh_token'])
                self.assertEqual(logi.auth_provider.access_token,
                                 dict_refresh_fixture['access_token'])

                await logi.close()

        self.loop.run_until_complete(run_test())

    def test_failed_authorization(self):
        """Test failed authorization."""
        logi = self.logi

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(AUTH_HOST, TOKEN_ENDPOINT, 'post',
                          aresponses.Response(status=401,
                                              text=self.fixtures['failed_authorization'],
                                              headers={'content-type': 'application/json'}))

                # Mock authorization, and verify AuthProvider state
                with self.assertRaises(AuthorizationFailed):
                    await logi.authorize('letmein')
                await logi.close()

        self.loop.run_until_complete(run_test())

    def test_token_persistence(self):
        """Test that token is loaded from the cache file implicitly."""

        # Write mock token to disk
        auth_fixture = json.loads(self.fixtures['auth_code'])
        token = {}
        token[self.client_id] = auth_fixture

        print(token)
        with open(self.cache_file, 'wb') as pickle_db:
            pickle.dump(token, pickle_db)

        auth_provider = AuthProvider(client_id=self.client_id,
                                     client_secret=self.client_secret,
                                     redirect_uri=self.redirect_uri,
                                     scopes=DEFAULT_SCOPES,
                                     cache_file=self.cache_file,
                                     logi_base=self.logi)

        self.assertTrue(
            auth_provider.authorized, 'API reports not authorized with token loaded from disk')
        self.assertEqual(
            auth_provider.refresh_token, auth_fixture['refresh_token']
        )
        self.assertEqual(
            auth_provider.access_token, auth_fixture['access_token']
        )
