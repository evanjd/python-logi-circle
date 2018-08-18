"""Camera class, representing a Logi Circle device"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
from datetime import datetime
import pytz
from .const import (
    PROTOCOL, ACCESSORIES_ENDPOINT, ACTIVITIES_ENDPOINT, IMAGES_ENDPOINT, JPEG_CONTENT_TYPE)
from .activity import Activity
from .utils import _stream_to_file
from .exception import UnexpectedContentType

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
            self._attrs['node_id'] = camera['nodeId']
            config = camera['configuration']
        except ValueError:
            _LOGGER.error(
                'Camera could not be initialised, API did not return one or more required properties.')
            raise

        # Optional attributes
        self._attrs['is_streaming'] = config.get(
            'streamingMode', 'off') == 'on'
        self._attrs['timezone'] = config.get('timeZone', 'UTC')
        self._attrs['battery_level'] = config.get('batteryLevel', None)
        self._attrs['is_charging'] = config.get('batteryCharging', None)
        self._attrs['model'] = config.get('modelNumber', 'Unknown')
        self._attrs['wifi_signal_strength'] = config.get(
            'wifiSignalStrength', None)
        self._attrs['firmware'] = config.get('firmwareVersion', None)
        if config.get('humidityIsAvailable', False):
            self._attrs['humidity'] = config.get('humidity', None)
        else:
            self._attrs['humidity'] = None
        if config.get('temperatureIsAvailable', False):
            self._attrs['temperature'] = config.get('temperature', None)
        else:
            self._attrs['temperature'] = None

        self._local_tz = pytz.timezone(self._attrs['timezone'])

    async def update(self):
        """Poll API for changes to camera properties"""
        _LOGGER.debug('Updating properties for camera %s', self.name)

        url = '%s/%s' % (ACCESSORIES_ENDPOINT, self.id)
        camera = await self._logi._fetch(
            url=url, method='GET')

        self._set_attributes(camera)

    async def query_activity_history(self, property_filter=None, date_filter=None, date_operator='<=', limit=100):
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

        raw_activitites = await self._logi._fetch(
            url=url, method='POST', request_body=payload)

        activities = []
        for raw_activity in raw_activitites['activities']:
            activity = Activity(camera=self, activity=raw_activity,
                                url=url, local_tz=self._local_tz, logi=self._logi)
            activities.append(activity)

        return activities

    @property
    async def last_activity(self):
        """Returns the most recent activity as an Activity object."""

        payload = {
            'limit': 1,
            'operator': '<=',
            'scanDirectionNewer': True
        }
        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.id, ACTIVITIES_ENDPOINT)

        raw_activity = await self._logi._fetch(
            url=url, method='POST', request_body=payload)

        try:
            unwrapped_activity = raw_activity['activities'][0]
            return Activity(camera=self, activity=unwrapped_activity, url=url, local_tz=self._local_tz, logi=self._logi)
        except IndexError:
            # If there's no activity history for this camera at all.
            return None

    @property
    def snapshot_url(self):
        """Returns the URL that provides a near realtime JPEG snapshot of what the camera sees"""
        url = '%s://%s/api%s/%s%s' % (PROTOCOL, self.node_id,
                                      ACCESSORIES_ENDPOINT, self.id, IMAGES_ENDPOINT)
        return url

    async def get_snapshot_image(self, filename=None):
        """Downloads a near realtime JPEG snapshot for this camera"""

        # Update camera before retrieving snapshot as node ID changes frequently
        await self.update()
        url = self.snapshot_url

        image = await self._logi._fetch(
            url=url, relative_to_api_root=False, raw=True)

        if image.content_type == JPEG_CONTENT_TYPE:
            # Got an image!

            if filename:
                # Stream to file
                await _stream_to_file(image.content, filename)
                image.close()
            else:
                # Return binary object
                content = await image.read()
                image.close()
                return content
        else:
            _LOGGER.error('Expected content-type %s, got %s when retrieving still image for camera %s',
                          JPEG_CONTENT_TYPE, image.content_type, self.name)
            raise UnexpectedContentType()

    async def set_power(self, status):
        """Disables streaming for this camera."""

        if status != 'on' and status != 'off':
            raise ValueError('"on" or "off" expected for status argument.')

        _LOGGER.debug('Setting power for %s to %s', self.name, status)

        url = '%s/%s' % (ACCESSORIES_ENDPOINT, self.id)
        payload = {"streamingMode": status}

        req = await self._logi._fetch(
            url=url, method='PUT', request_body=payload, raw=True)

        if req.status < 300:
            self._attrs['is_streaming'] = status == 'on'
            return True
        else:
            return False

    @property
    def id(self):
        """Return device ID."""
        return self._attrs.get('id')

    @property
    def node_id(self):
        """Return device node ID."""
        return self._attrs.get('node_id')

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
        """Return bool indicating whether device is online and can accept commands (hard "on")."""
        return self._attrs.get('is_connected')

    @property
    def is_streaming(self):
        """Return bool indicating whether device is streaming video (soft "on")."""
        return self._attrs.get('is_streaming')

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

    @property
    def temperature(self):
        """Return temperature (returns None if not supported by device)."""
        return self._attrs.get('temperature')

    @property
    def humidity(self):
        """Return relative humidity (returns None if not supported by device)."""
        return self._attrs.get('humidity')
