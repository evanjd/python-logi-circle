# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import json
from unittest.mock import MagicMock
from datetime import datetime
import aresponses
import pytz
from aiohttp.client_exceptions import ClientResponseError
from tests.test_base import LogiUnitTestBase
from logi_circle.activity import Activity
from logi_circle.camera import Camera
from logi_circle.const import (API_HOST,
                               API_BASE,
                               ACCESSORIES_ENDPOINT,
                               CONFIG_ENDPOINT,
                               ISO8601_FORMAT_MASK,
                               ACCEPT_IMAGE_HEADER,
                               ACCEPT_VIDEO_HEADER,
                               ACTIVITY_IMAGE_ENDPOINT,
                               ACTIVITY_MP4_ENDPOINT,
                               ACTIVITY_DASH_ENDPOINT,
                               ACTIVITY_HLS_ENDPOINT)
from .helpers import async_return

BASE_ACTIVITY_URL = '/abc123'
TEST_TZ = 'Etc/GMT+10'


class TestActivity(LogiUnitTestBase):
    """Unit test for the Activity class."""

    def test_activity_props(self):
        activity_json = json.loads(self.fixtures['activity'])

        activity = Activity(activity=activity_json,
                            logi=self.logi,
                            url=BASE_ACTIVITY_URL,
                            local_tz=pytz.timezone(TEST_TZ))

        # Test props match fixture
        self.assertEqual(activity.activity_id, activity_json['activityId'])
        self.assertEqual(activity.duration.seconds, activity_json['playbackDuration'] / 1000)
        self.assertEqual(activity.start_time_utc,
                         datetime.strptime(activity_json['startTime'], ISO8601_FORMAT_MASK))
        self.assertEqual(activity.end_time_utc,
                         datetime.strptime(activity_json['endTime'], ISO8601_FORMAT_MASK))
        self.assertEqual(activity.start_time,
                         activity.start_time_utc.replace(
                             tzinfo=pytz.utc).astimezone(activity._local_tz))
        self.assertEqual(activity.end_time,
                         activity.end_time_utc.replace(
                             tzinfo=pytz.utc).astimezone(activity._local_tz))

    def test_activity_assets(self):
        activity_json = json.loads(self.fixtures['activity'])

        activity = Activity(activity=activity_json,
                            logi=self.logi,
                            url=BASE_ACTIVITY_URL,
                            local_tz=pytz.timezone(TEST_TZ))

        # Test props match fixture
        url_base = '%s%s/%s' % (API_BASE, BASE_ACTIVITY_URL, activity_json['activityId'])
        self.assertEqual(activity.jpeg_url, url_base + ACTIVITY_IMAGE_ENDPOINT)
        self.assertEqual(activity.mp4_url, url_base + ACTIVITY_MP4_ENDPOINT)
        self.assertEqual(activity.hls_url, url_base + ACTIVITY_HLS_ENDPOINT)
        self.assertEqual(activity.dash_url, url_base + ACTIVITY_DASH_ENDPOINT)

        my_file = 'myfile.file'

        activity._get_file = MagicMock(
            return_value=async_return(None))

        async def run_test():
            # Image
            await activity.download_jpeg(my_file)
            activity._get_file.assert_called_with(url=activity.jpeg_url,
                                                  filename=my_file,
                                                  accept_header=ACCEPT_IMAGE_HEADER)

            # Video
            await activity.download_mp4(my_file)
            activity._get_file.assert_called_with(url=activity.mp4_url,
                                                  filename=my_file,
                                                  accept_header=ACCEPT_VIDEO_HEADER)

            # Dash
            await activity.download_dash(my_file)
            activity._get_file.assert_called_with(url=activity.dash_url,
                                                  filename=my_file)

            # HLS
            await activity.download_hls(my_file)
            activity._get_file.assert_called_with(url=activity.hls_url,
                                                  filename=my_file)

        self.loop.run_until_complete(run_test())
