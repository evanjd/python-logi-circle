"""Camera class, representing a Logi Circle device"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
from datetime import datetime, timedelta
import pytz
from aiohttp.client_exceptions import ClientResponseError
from .const import (ACCESSORIES_ENDPOINT,
                    ACTIVITIES_ENDPOINT,
                    CONFIG_ENDPOINT,
                    PROP_MAP,
                    FEATURES_MAP,
                    ACTIVITY_API_LIMIT,
                    GEN_1_MODEL,
                    GEN_2_MODEL,
                    GEN_1_MOUNT,
                    GEN_2_MOUNT_WIRE,
                    GEN_2_MOUNT_WIREFREE,
                    MOUNT_UNKNOWN)
from .live_stream import LiveStream
from .activity import Activity
from .utils import _slugify_string

_LOGGER = logging.getLogger(__name__)


class Camera():
    """Generic implementation for Logi Circle camera."""

    def __init__(self, logi, camera):
        """Initialise Logi Camera object."""
        self.logi = logi
        self._attrs = {}
        self._live_stream = None
        self._current_activity = None
        self._last_activity = None
        self._next_update_time = datetime.utcnow()

        self._set_attributes(camera)

    def _set_attributes(self, camera):
        """Sets attrs property based on mapping defined in PROP_MAP constant"""
        config = camera['configuration']

        for internal_prop, api_mapping in PROP_MAP.items():
            base_obj = config if api_mapping.get('config') else camera
            value = base_obj.get(api_mapping['key'], api_mapping.get('default_value'))

            if value is None and api_mapping.get('required'):
                raise KeyError("Mandatory property '%s' missing from camera JSON." %
                               (api_mapping['key']))

            self._attrs[internal_prop] = value

        self._local_tz = pytz.timezone(self.timezone)
        self._live_stream = LiveStream(logi=self.logi, camera=self)

    async def subscribe(self, event_types):
        """Shorthand method for subscribing to a single camera's events."""
        return self.logi.subscribe(event_types, [self])

    async def update(self, force=False):
        """Poll API for changes to camera properties."""
        _LOGGER.debug('Updating properties for camera %s', self.name)

        update_throttle = self.logi.update_throttle

        if force is True or datetime.utcnow() >= self._next_update_time:
            url = "%s/%s" % (ACCESSORIES_ENDPOINT, self.id)
            camera = await self.logi._fetch(url=url)
            self._set_attributes(camera)
            self._next_update_time = datetime.utcnow(
            ) + timedelta(seconds=update_throttle)
        else:
            _LOGGER.debug('Request to update ignored, next update is permitted at %s.',
                          self._next_update_time)

    async def set_config(self, prop, value):
        """Internal method for updating the camera's configuration."""
        external_prop = PROP_MAP.get(prop)

        if external_prop is None or not external_prop.get("settable", False):
            raise NameError("Property '%s' is not settable." % (prop))

        url = "%s/%s%s" % (ACCESSORIES_ENDPOINT, self.id, CONFIG_ENDPOINT)
        payload = {external_prop['key']: value}

        _LOGGER.debug("Setting %s (%s) to %s", prop, external_prop['key'], str(value))

        try:
            await self.logi._fetch(
                url=url,
                method="PUT",
                request_body=payload)

            self._attrs[prop] = value
            _LOGGER.debug("Successfully set %s to %s", prop,
                          str(value))
        except ClientResponseError as error:
            _LOGGER.error(
                "Status code %s returned when updating %s to %s", error.status, prop, str(value))
            raise

    async def query_activity_history(self,
                                     property_filter=None,
                                     date_filter=None,
                                     date_operator='<=',
                                     limit=ACTIVITY_API_LIMIT):
        """Filter the activity history, returning Activity objects for any matching result."""

        if limit > ACTIVITY_API_LIMIT:
            # Logi Circle API rejects requests where the limit exceeds 100, so we'll guard for that here.
            raise ValueError(
                'Limit may not exceed %s due to API restrictions.' % (ACTIVITY_API_LIMIT))
        if date_filter is not None and not isinstance(date_filter, datetime):
            raise TypeError('date_filter must be a datetime object.')

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

        raw_activitites = await self.logi._fetch(
            url=url, method='POST', request_body=payload)

        activities = []
        for raw_activity in raw_activitites['activities']:
            activity = Activity(activity=raw_activity,
                                url=url,
                                local_tz=self._local_tz,
                                logi=self.logi)
            activities.append(activity)

        return activities

    @property
    def supported_features(self):
        """Returns an array of supported sensors for this camera."""
        return FEATURES_MAP[self.mount]

    def supports_feature(self, feature):
        """Returns a bool indicating whether a given sensor is implemented for this camera."""
        return feature in self.supported_features

    @property
    def current_activity(self):
        """Returns the current open activity - only available when subscribed to activity events."""

        if (self._current_activity and
                self._current_activity.start_time_utc >= (datetime.utcnow() - timedelta(minutes=3))):
            # Only return activities that began in the last 3 minutes, as this is the maximum length of an activity
            return self._current_activity
        return None

    async def get_last_activity(self, force_refresh=False):
        """Returns the most recent activity as an Activity object."""
        if self._last_activity is None or force_refresh:
            return await self._pull_last_activity()
        return self._last_activity

    async def _pull_last_activity(self):
        """Queries API for latest activity"""
        activity = await self.query_activity_history(limit=1)

        try:
            self._last_activity = activity[0]
            return self._last_activity
        except IndexError:
            # If there's no activity history for this camera at all.
            return None

    @property
    def live_stream(self):
        """Return LiveStream class for this camera."""
        return self._live_stream

    @property
    def id(self):
        """Return device ID."""
        return self._attrs.get('id')

    @property
    def name(self):
        """Return device name."""
        return self._attrs.get('name')

    @property
    def slugify_safe_name(self):
        """Returns device name (falling back to device ID if name cannot be slugified)"""
        raw_name = self.name
        if _slugify_string(raw_name):
            # Return name if has > 0 chars after being slugified
            return raw_name
        # Fallback to camera ID
        return self.id

    @property
    def timezone(self):
        """Return timezone offset."""
        return self._attrs.get('timezone')

    @property
    def connected(self):
        """Return bool indicating whether device is online and can accept commands (hard "on")."""
        return self._attrs.get('connected')

    @property
    def streaming(self):
        """Return streaming mode for camera (soft "on")."""
        return self._attrs.get('streaming')

    @property
    def battery_level(self):
        """Return battery level (integer between -1 and 100)."""
        # -1 means no battery, wired only.
        return self._attrs.get('battery_level')

    @property
    def battery_saving(self):
        """Return whether battery saving mode is activated."""
        return self._attrs.get('battery_saving')

    @property
    def charging(self):
        """Return bool indicating whether the device is currently charging."""
        return self._attrs.get('charging')

    @property
    def model(self):
        """Return model number."""
        return self._attrs.get('model')

    @property
    def mount(self):
        """Infer mount type from camera model and battery level."""
        if self.model == GEN_1_MODEL:
            return GEN_1_MOUNT
        if self.model == GEN_2_MODEL:
            if self.battery_level == -1:
                return GEN_2_MOUNT_WIRE
            return GEN_2_MOUNT_WIREFREE
        return MOUNT_UNKNOWN

    @property
    def firmware(self):
        """Return firmware version."""
        return self._attrs.get('firmware')

    @property
    def signal_strength_percentage(self):
        """Return signal strength between 0-100 (0 = bad, 100 = excellent)."""
        return self._attrs.get('signal_strength_percentage')

    @property
    def signal_strength_category(self):
        """Interpret signal strength value and return a friendly categorisation."""
        signal_strength = self._attrs.get('signal_strength_percentage')
        if signal_strength is not None:
            if signal_strength > 80:
                return 'Excellent'
            if signal_strength > 60:
                return 'Good'
            if signal_strength > 40:
                return 'Fair'
            if signal_strength > 20:
                return 'Poor'
            return 'Bad'
        return None

    @property
    def mac_address(self):
        """Return MAC address for camera's WiFi interface."""
        return self._attrs.get('mac_address')

    @property
    def microphone(self):
        """Return bool indicating whether microphone is enabled."""
        return self._attrs.get('microphone')

    @property
    def microphone_gain(self):
        """Return microphone gain using absolute scale (1-100)."""
        return self._attrs.get('microphone_gain')

    @property
    def pir_wake_up(self):
        """Returns bool indicating whether camera can operate in low power PIR
           wake up mode."""
        return self._attrs.get('pir_wake_up')

    @property
    def speaker(self):
        """Return bool indicating whether speaker is currently enabled."""
        return self._attrs.get('speaker')

    @property
    def speaker_volume(self):
        """Return speaker volume using absolute scale (1-100)."""
        return self._attrs.get('speaker_volume')

    @property
    def led(self):
        """Return bool indicating whether LED is enabled."""
        return self._attrs.get('led')

    @property
    def recording(self):
        """Return bool indicating whether recording mode is enabled."""
        return not self._attrs.get('recording_disabled')
