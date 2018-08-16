# coding: utf-8
# vim:sw=4:ts=4:et:
from datetime import datetime, timedelta
import logging
import pytz
from logi_circle.const import (ISO8601_FORMAT_MASK)

_LOGGER = logging.getLogger(__name__)


class Activity(object):

    def __init__(self, camera, activity, url, local_tz, logi):
        """Initialize Activity object."""
        self._camera = camera
        self._logi = logi
        self._attrs = {}
        self._local_tz = local_tz
        self._url = url
        self._set_attributes(activity)

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
    def download_url(self):
        """Returns the download URL for the current activity."""
        return '%s/%s/mp4' % (self._url, self.activity_id)

    def download(self, filename=None):
        """Download the activity as an MP4, optionally saving to disk."""
        url = self.download_url

        req = self._logi.query(url=url, method='GET', raw=True)
        req.raise_for_status()

        if filename:
            with open(filename, 'wb+') as recording:
                recording.write(req.content)
                return
        else:
            return req.content

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
