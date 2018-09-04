# -*- coding: utf-8 -*-
"""Tests for the Logi API LiveStream class."""
from datetime import datetime, timedelta
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT, ACCESSORIES_ENDPOINT, LIVESTREAM_ENDPOINT
from freezegun import freeze_time


class TestLiveStream(LogiUnitTestBase):
    """Unit test for the LiveStream class."""

    @freeze_time("2018-01-01")
    def test_initialise(self):
        """Test initialise method (and all its dependent methods)"""
        logi = self.logi_no_reuse

        # This is effectively an integration test rather than a unit test.
        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT + '/mock-camera', 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessory'],
                                              headers={'content-type': 'application/json'}))
                arsps.add('node-mocked-2.video.logi.com', '/api' + ACCESSORIES_ENDPOINT + '/mock-camera' + LIVESTREAM_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['mpd'],
                                              headers={'content-type': 'application/json'}))
                arsps.add('node-mocked-2.video.logi.com', '/api' + ACCESSORIES_ENDPOINT + '/mock-camera' + '/init.mp4', 'get',
                          aresponses.Response(status=200,
                                              text='0',
                                              headers={'content-type': 'video/mp4'}))

                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]

                # Get live stream
                live_stream = camera.live_stream

                # Verify uninitialised state
                self.assertFalse(
                    live_stream._initialised, 'Initialised is not False')

                # Initialise stream
                await live_stream._initialise()

                # Check properties against mocked DASH stream definition
                base_url = 'https://node-mocked-2.video.logi.com:443/api/accessories/mock-camera/'
                self.assertEqual(
                    live_stream._mpd_data['base_url'], base_url, 'Base URL mismatch')
                self.assertEqual(
                    live_stream._mpd_data['header_url'], 'init.mp4?requestId=abc', 'Init MP4 URI mismatch')
                self.assertEqual(
                    live_stream._mpd_data['stream_filename_template'], 'clip_000001_$Number$.mp4?requestId=abc', 'Stream filename template mismatch')
                self.assertEqual(
                    live_stream._mpd_data['start_index'], 1, 'Start index mismatch')
                self.assertEqual(
                    live_stream._index, 1, 'Start index mismatch')
                self.assertEqual(
                    live_stream._mpd_data['segment_length'], 4500, 'Segment duration mismatch')

                # Check mocked init MP4 is present
                self.assertIsNotNone(
                    live_stream._initialisation_file, 'Init file is null')

                # Check initialised state is set
                self.assertTrue(
                    live_stream._initialised, 'Initialised is not True')

                # Check next segment time is correct
                self.assertEqual(
                    live_stream._next_segment_time, datetime.now() + timedelta(milliseconds=4500))

                # Verify time until next segment is correct
                self.assertEqual(
                    live_stream._get_time_before_next_segment(), 4.5)

        self.loop.run_until_complete(run_test())
