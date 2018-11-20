# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
from unittest.mock import patch
import aresponses
import aiohttp
from tests.test_base import LogiUnitTestBase
from logi_circle import LogiCircle
from logi_circle.const import AUTH_HOST, TOKEN_ENDPOINT, API_HOST, ACCESSORIES_ENDPOINT, DEFAULT_FFMPEG_BIN
from logi_circle.exception import NotAuthorized, AuthorizationFailed


class TestAuth(LogiUnitTestBase):
    """Unit test for core Logi class."""

    def test_fetch_no_auth(self):
        """Fetch should return NotAuthorized if no access token is present"""
        logi = self.logi

        async def run_test():
            with self.assertRaises(NotAuthorized):
                await logi._fetch(url='/api')

        self.loop.run_until_complete(run_test())

    def test_fetch_with_auth(self):
        """Fetch should process request if user is authorized"""
        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=200,
                                              text='{ "abc" : 123 }',
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api', 'post',
                          aresponses.Response(status=200,
                                              text='{ "foo" : "bar" }',
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api', 'put',
                          aresponses.Response(status=200,
                                              text='{ "success" : true }',
                                              headers={'content-type': 'application/json'}))
                get_result = await logi._fetch(url='/api')
                post_result = await logi._fetch(url='/api', method='POST')
                put_result = await logi._fetch(url='/api', method='PUT')
                self.assertEqual(get_result['abc'], 123)
                self.assertEqual(post_result['foo'], 'bar')
                self.assertTrue(put_result['success'])

        self.loop.run_until_complete(run_test())

    def test_fetch_token_refresh(self):
        """Fetch should refresh token if it expires"""
        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()
        auth_fixture = self.fixtures['auth_code']

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=401))
                arsps.add(AUTH_HOST, TOKEN_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=auth_fixture,
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=200,
                                              text='{ "foo" : "bar" }',
                                              headers={'content-type': 'application/json'}))

                get_result = await logi._fetch(url='/api')
                self.assertEqual(get_result['foo'], 'bar')

        self.loop.run_until_complete(run_test())

    def test_fetch_guard_infinite_loop(self):
        """Fetch should bail out if request 401s immediately after token refresh"""
        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()
        auth_fixture = self.fixtures['auth_code']

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=401))
                arsps.add(AUTH_HOST, TOKEN_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=auth_fixture,
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=401))

                with self.assertRaises(AuthorizationFailed):
                    await logi._fetch(url='/api')

        self.loop.run_until_complete(run_test())

    def test_fetch_raw(self):
        """Fetch should return ClientResponse object if raw parameter set"""
        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api', 'get',
                          aresponses.Response(status=200))

                raw = await logi._fetch(url='/api', raw=True)
                self.assertIsInstance(raw, aiohttp.ClientResponse)

                raw.close()

        self.loop.run_until_complete(run_test())

    def test_fetch_invalid_method(self):
        """Fetch should raise ValueError for unsupported methods"""

        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()

        async def run_test():
            with self.assertRaises(ValueError):
                await logi._fetch(url='/api', method='TEAPOT')

        self.loop.run_until_complete(run_test())

    def test_get_cameras(self):
        """Camera property should return 3 cameras"""

        logi = self.logi
        logi.auth_provider = self.get_authorized_auth_provider()

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, ACCESSORIES_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                cameras = await logi.cameras
                self.assertEqual(len(cameras), 3)

        self.loop.run_until_complete(run_test())
    
    def test_ffmpeg_valid(self):
        """Resolved ffmpeg path should be set if ffmpeg binary detected"""
        
        logi = self.logi

        # Patch subprocess so that it always returns nothing (implicit success)
        with patch('subprocess.check_call'):
            # Default value should be used if ffmpeg unset.
            self.assertEqual(logi._get_ffmpeg_path(), DEFAULT_FFMPEG_BIN)

            # Input ffmpeg_bin should be respected if valid
            self.assertEqual(logi._get_ffmpeg_path('groovy_ffmpeg'), 'groovy_ffmpeg')

            # Test property on class.
            logi_default_ffmpeg = LogiCircle(client_id="bud",
                                     client_secret="wei",
                                     api_key="serrrrr",
                                     redirect_uri="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            self.assertEqual(logi_default_ffmpeg.ffmpeg_path, DEFAULT_FFMPEG_BIN)
            logi_custom_ffmpeg = LogiCircle(client_id="bud",
                                     client_secret="wei",
                                     api_key="serrrrr",
                                     redirect_uri="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                     ffmpeg_path="super_cool_ffmpeg")
            self.assertEqual(logi_custom_ffmpeg.ffmpeg_path, "super_cool_ffmpeg")
            
    def test_ffmpeg_invalid(self):
        """Resolved ffmpeg path should None if ffmpeg missing"""

        logi = self.logi

        # Test function
        ffmpeg_path = logi._get_ffmpeg_path('this-is-not-ffmpeg')
        self.assertIsNone(ffmpeg_path)

        # Test property on class.
        logi_bad_ffmpeg = LogiCircle(client_id="bud",
                                     client_secret="wei",
                                     api_key="serrrrr",
                                     redirect_uri="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                                     ffmpeg_path="this-still-is-not-ffmpeg")

        self.assertIsNone(logi_bad_ffmpeg.ffmpeg_path)