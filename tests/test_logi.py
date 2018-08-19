# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT


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
        """Test explicit login (don't use cached cookie)"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                await logi.login()
                self.assertTrue(
                    logi.is_connected, 'API reports not connected after successful login')

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
