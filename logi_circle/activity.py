"""Activity class, represents activity observed by your camera (maximum 3 minutes)"""
# coding: utf-8
# vim:sw=4:ts=4:et:
from datetime import datetime, timedelta
import logging
import pytz
from .const import (ISO8601_FORMAT_MASK,
                    API_BASE,
                    ACCEPT_IMAGE_HEADER,
                    ACCEPT_VIDEO_HEADER,
                    ACTIVITY_IMAGE_ENDPOINT,
                    ACTIVITY_MP4_ENDPOINT,
                    ACTIVITY_DASH_ENDPOINT,
                    ACTIVITY_HLS_ENDPOINT)
from .utils import _stream_to_file

_LOGGER = logging.getLogger(__name__)


class Activity():
    """Generic implementation for a Logi Circle activity."""

    def __init__(self, activity, url, local_tz, logi):
        """Initialize Activity object."""
        self._logi = logi
        self._attrs = {}
        self._local_tz = local_tz
        self._set_attributes(activity)
        self._base_url = '%s%s/%s' % (API_BASE, url, self.activity_id)

    def _set_attributes(self, activity):
        self._attrs['activity_id'] = activity['activityId']
        self._attrs['relevance_level'] = activity['relevanceLevel']

        raw_start_time = activity['startTime']
        raw_end_time = activity['endTime']
        raw_duration = activity['playbackDuration']

        self._attrs['start_time_utc'] = datetime.strptime(
            raw_start_time, ISO8601_FORMAT_MASK)
        self._attrs['end_time_utc'] = datetime.strptime(
            raw_end_time, ISO8601_FORMAT_MASK)

        self._attrs['start_time'] = self._attrs['start_time_utc'].replace(
            tzinfo=pytz.utc).astimezone(self._local_tz)
        self._attrs['end_time'] = self._attrs['end_time_utc'].replace(
            tzinfo=pytz.utc).astimezone(self._local_tz)

        self._attrs['duration'] = timedelta(milliseconds=raw_duration)

    @property
    def jpeg_url(self):
        """Returns the JPEG download URL for the current activity."""
        return '%s%s' % (self._base_url, ACTIVITY_IMAGE_ENDPOINT)

    @property
    def mp4_url(self):
        """Returns the MP4 download URL for the current activity."""
        return '%s%s' % (self._base_url, ACTIVITY_MP4_ENDPOINT)

    @property
    def hls_url(self):
        """Returns the HLS playlist download URL for the current activity."""
        return '%s%s' % (self._base_url, ACTIVITY_HLS_ENDPOINT)

    @property
    def dash_url(self):
        """Returns the DASH manifest download URL for the current activity."""
        return '%s%s' % (self._base_url, ACTIVITY_DASH_ENDPOINT)

    async def download_jpeg(self, filename=None):
        """Download the activity as a JPEG, optionally saving to disk."""
        return await self._get_file(url=self.jpeg_url,
                                    filename=filename,
                                    accept_header=ACCEPT_IMAGE_HEADER)

    async def download_mp4(self, filename=None):
        """Download the activity as an MP4, optionally saving to disk."""
        return await self._get_file(url=self.mp4_url,
                                    filename=filename,
                                    accept_header=ACCEPT_VIDEO_HEADER)

    async def download_hls(self, filename=None):
        """Download the activity's HLS playlist, optionally saving to disk."""
        return await self._get_file(url=self.hls_url,
                                    filename=filename)

    async def download_dash(self, filename=None):
        """Download the activity's DASH manifest, optionally saving to disk."""
        return await self._get_file(url=self.dash_url,
                                    filename=filename)

    async def _get_file(self, url, filename=None, accept_header=None):
        """Download the specified URL, optionally saving to disk."""
        asset = await self._logi._fetch(url=url,
                                        headers=accept_header,
                                        raw=True,
                                        relative_to_api_root=False)

        if filename:
            # Stream to file
            await _stream_to_file(asset.content, filename)
            asset.close()
        else:
            # Return binary object
            content = await asset.read()
            asset.close()
            return content

    @property
    def activity_id(self):
        """Return activity ID."""
        return self._attrs['activity_id']

    @property
    def start_time(self):
        """Return start time as datetime object, local to the camera's timezone."""
        return self._attrs['start_time']

    @property
    def end_time(self):
        """Return end time as datetime object, local to the camera's timezone."""
        return self._attrs['end_time']

    @property
    def start_time_utc(self):
        """Return start time as datetime object in the UTC timezone."""
        return self._attrs['start_time_utc']

    @property
    def end_time_utc(self):
        """Return end time as datetime object in the UTC timezone."""
        return self._attrs['end_time_utc']

    @property
    def duration(self):
        """Return activity duration as a timedelta object."""
        return self._attrs['duration']

    @property
    def relevance_level(self):
        """Return relevance level."""
        return self._attrs['relevance_level']
