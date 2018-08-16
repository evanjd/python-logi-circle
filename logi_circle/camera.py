# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import pytz
from datetime import datetime
from logi_circle.const import (ACCESSORIES_ENDPOINT, ACTIVITIES_ENDPOINT)
from logi_circle.activity import Activity

_LOGGER = logging.getLogger(__name__)


class Camera(object):
    """Generic implementation for Logi Circle camera."""

    def __init__(self, logi, camera):
        """Initialise Logi Camera object."""
        self._logi = logi
        self._attrs = {}

        self._set_attributes(camera)

    def _set_attributes(self, camera):
        config = None

        # Mandatory attributes
        try:
            self._attrs['id'] = camera['accessoryId']
            self._attrs['name'] = camera['name']
            self._attrs['is_connected'] = camera['isConnected']
            config = camera['configuration']
        except ValueError:
            _LOGGER.error(
                'Camera could not be initialised, API did not return one or more required properties.')
            raise

        # Optional attributes
        self._attrs['timezone'] = config.get('timeZone', 'UTC')
        self._attrs['battery_level'] = config.get('batteryLevel', None)
        self._attrs['is_charging'] = config.get('batteryCharging', None)
        self._attrs['model'] = config.get('modelNumber', 'Unknown')
        self._attrs['wifi_signal_strength'] = config.get(
            'wifiSignalStrength', None)
        self._attrs['firmware'] = config.get('firmwareVersion', None)
        if (config.get('humidityIsAvailable', False)):
            self._attrs['humidity'] = config.get('humidity', None)
        if (config.get('temperatureIsAvailable', False)):
            self._attrs['temperature'] = config.get('temperature', None)

        self._local_tz = pytz.timezone(self._attrs['timezone'])

    def query_activity_history(self, property_filter=None, date_filter=None, date_operator='<=', limit=100):
        """Filter the activity history, returning Activity objects for any matching result."""

        if limit > 100:
            # Logi Circle API rejects requests where the limit exceeds 100, so we'll guard for that here.
            raise ValueError(
                'Limit may not exceed 100 due to API restrictions.')
        if date_filter is not None and not isinstance(date_filter, datetime):
            raise ValueError('date_filter must be a datetime object.')

        # Base payload object
        payload = {
            'limit': limit,
            'scanDirectionNewer': True
        }
        if date_filter:
            # Date filters are expressed using the same format for activity ID keys (YYYYMMDD"T"HHMMSSZ).
            # Let's convert our date_filter to match.

            # If timezone unaware, assume it's local to the camera's timezone.
            date_filter_tz = date_filter.tzinfo or self._local_tz

            # Activity ID keys are always expressed in UTC, so cast to UTC first.
            utc_date_filter = date_filter.replace(
                tzinfo=date_filter_tz).astimezone(pytz.utc)
            payload['startActivityId'] = utc_date_filter.strftime(
                '%Y%m%dT%H%M%SZ')

            payload['operator'] = date_operator

        if property_filter:
            payload['filter'] = property_filter

        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.id, ACTIVITIES_ENDPOINT)

        raw_activitites = self._logi.query(
            url=url, method='POST', request_body=payload)

        activities = []
        for raw_activity in raw_activitites['activities']:
            activity = Activity(camera=self, activity=raw_activity,
                                url=url, local_tz=self._local_tz, logi=self._logi)
            activities.append(activity)

        return activities

    @property
    def last_activity(self):
        """Returns the most recent activity as an Activity object."""

        payload = {
            'limit': 1,
            'operator': '<=',
            'scanDirectionNewer': True
        }
        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.id, ACTIVITIES_ENDPOINT)

        raw_activity = self._logi.query(
            url=url, method='POST', request_body=payload)

        try:
            unwrapped_activity = raw_activity['activities'][0]
            return Activity(camera=self, activity=unwrapped_activity, url=url, local_tz=self._local_tz, logi=self._logi)
        except IndexError:
            # If there's no activity history for this camera at all.
            return None

    @property
    def id(self):
        """Return device ID."""
        return self._attrs.get('id')

    @property
    def name(self):
        """Return device name."""
        return self._attrs.get('name')

    @property
    def timezone(self):
        """Return timezone offset."""
        return self._attrs.get('timezone')

    @property
    def is_connected(self):
        """ Return bool indicating whether device is online and capable of returning video. """
        return self._attrs.get('is_connected')

    @property
    def battery_level(self):
        """Return battery level (integer between 0-100)."""
        return self._attrs.get('battery_level')

    @property
    def is_charging(self):
        """Return bool indicating whether the device is currently connected to power."""
        return self._attrs.get('is_charging')

    @property
    def model(self):
        """Return model number."""
        return self._attrs.get('model')

    @property
    def signal_strength_percentage(self):
        """Return signal strength between 0-100 (0 = bad, 100 = excellent)."""
        return self._attrs.get('wifi_signal_strength')

    @property
    def signal_strength_category(self):
        """Interpret signal strength value and return a friendly categorisation."""
        signal_strength = self._attrs.get('wifi_signal_strength', 0)
        if signal_strength > 80:
            return 'Excellent'
        if signal_strength > 60:
            return 'Good'
        if signal_strength > 40:
            return 'Fair'
        if signal_strength > 20:
            return 'Poor'
        return 'Bad'
