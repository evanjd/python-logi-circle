# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT, VALIDATE_ENDPOINT, COOKIE_NAME
from logi_circle.utils import _save_cache, _read_cache


class TestLogi(LogiUnitTestBase):
    """Unit test for core Logi class."""

    def test_prelogin_state(self):
        """Validate pre-login state"""
        logi = self.logi
        # Should start false, no login performed yet.
        self.assertFalse(logi.is_connected)
        # No session obviously
        self.assertIsNone(logi._session)
        # User/pass should match what it was initalised with.
        self.assertEqual(logi.username, self.username)
        self.assertEqual(logi.password, self.password)

    def test_auth(self):
        """Test explicit login and logout (don't use cached cookie)"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                await logi.login()
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after successful login')
                self.assertIsNotNone(
                    logi._session, 'Session not created after successful login')
                await logi.logout()
                self.assertFalse(
                    logi.is_connected, 'API reports still connected after logout')
                self.assertIsNone(
                    logi._session, 'Session still exists after logout')

        self.loop.run_until_complete(run_test())

    def test_cookie_reuse(self):
        """Test cached cookie retrieval"""
        _save_cache({'account': self.username, 'cookie': 'MOCK'},
                    self.cache_file)
        logi = self.logi

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + VALIDATE_ENDPOINT, 'get',
                          aresponses.Response(status=200))
                await logi.login()
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after restoring cached session')
                self.assertIsNotNone(
                    logi._session, 'Session not created after restoring cached session')

        self.loop.run_until_complete(run_test())

    def test_cookie_save(self):
        """Test that new cookie is cached after successful login"""
        logi = self.logi

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200, headers={'Set-Cookie': '%s=MOCK_COOKIE' % (COOKIE_NAME)}))
                await logi.login()
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after successful login')
                self.assertIsNotNone(
                    logi._session, 'Session not created after successful login')
                saved_cookie = _read_cache(self.cache_file)
                self.assertEqual(saved_cookie['account'], self.username)
                self.assertEqual(saved_cookie['cookie'], 'MOCK_COOKIE')

        self.loop.run_until_complete(run_test())

    def test_get_cameras(self):
        """Test implicit login performed when grabbing cameras"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                # Perform implicit login, and get camera
                cameras = await logi.cameras

                # Implict login successful
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after implicit login')

                # Has 1 camera
                self.assertEqual(
                    len(cameras), 1, 'Wrong number of cameras returned')

        self.loop.run_until_complete(run_test())

    def test_session_healing(self):
        """Test that session is transparently re-established if it expires"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                # Login response
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                # Cameras response (success)
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                # Cameras response (401, need to reauth)
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=401))
                # Reauth response
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                # Cameras response (success)
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                # Perform implicit login, and get camera (throw away result)
                await logi.cameras
                # Do it again, session has expired. Should still return 1 camera after re-establishing session.
                cameras = await logi.cameras

                # Has 1 camera
                self.assertEqual(
                    len(cameras), 1, 'Wrong number of cameras returned')

        self.loop.run_until_complete(run_test())
