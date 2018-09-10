"""Camera class, representing a Logi Circle device"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import os
from datetime import datetime, timedelta
from subprocess import CalledProcessError
from tempfile import NamedTemporaryFile
import pytz
from aiohttp.client_exceptions import ClientResponseError
from .const import (
    PROTOCOL, ACCESSORIES_ENDPOINT, ACTIVITIES_ENDPOINT, IMAGES_ENDPOINT, JPEG_CONTENT_TYPE, FEATURES,
    MODEL_GEN_1, MODEL_GEN_2, MODEL_GEN_1_NAME, MODEL_GEN_2_NAME, MODEL_GEN_UNKNOWN_NAME,
    MODEL_GEN_1_MOUNT, MODEL_GEN_2_MOUNT_WIRED, MODEL_GEN_2_MOUNT_WIRELESS,
    UPDATE_REQUEST_THROTTLE)
from .activity import Activity
from .live_stream import LiveStream
from .utils import (_stream_to_file, _write_to_file, _delete_quietly, _get_file_duration,
                    _get_first_frame_from_video, _truncate_video, requires_ffmpeg)
from .exception import UnexpectedContentType

_LOGGER = logging.getLogger(__name__)


class Camera():
    """Generic implementation for Logi Circle camera."""

    def __init__(self, logi, camera):
        """Initialise Logi Camera object."""
        self._logi = logi
        self._attrs = {}
        # Internal prop to determine when the next update is allowed.
        self._next_update_time = datetime.utcnow()

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
        self._attrs['streaming_mode'] = config.get(
            'streamingMode', 'off') != 'off'
        self._attrs['timezone'] = config.get('timeZone', 'UTC')
        self._attrs['battery_level'] = config.get('batteryLevel', None)
        self._attrs['is_charging'] = config.get('batteryCharging', None)
        self._attrs['battery_saving'] = config.get('saveBattery', None)
        self._attrs['model'] = config.get('modelNumber', 'Unknown')
        self._attrs['wifi_signal_strength'] = config.get(
            'wifiSignalStrength', None)
        self._attrs['firmware'] = config.get('firmwareVersion', None)
        self._attrs['ip_address'] = config.get('ipAddress', None)
        self._attrs['mac_address'] = config.get('macAddress', None)
        self._attrs['wifi_ssid'] = config.get('wifiSsid', None)
        self._attrs['microphone_on'] = config.get('microphoneOn', False)
        self._attrs['microphone_gain'] = config.get('microphoneGain', None)
        self._attrs['speaker_on'] = config.get('speakerOn', False)
        self._attrs['speaker_volume'] = config.get('speakerVolume', None)
        self._attrs['led'] = config.get('ledEnabled', False)
        self._attrs['privacy_mode'] = config.get('privacyMode', False)
        self._attrs['plan_name'] = camera.get('planName', False)

        # These sensors don't appear to be present on any devices sold in the market today.
        if config.get('humidityIsAvailable', False):
            self._attrs['humidity'] = config.get('humidity', None)
        else:
            self._attrs['humidity'] = None
        if config.get('temperatureIsAvailable', False):
            self._attrs['temperature'] = config.get('temperature', None)
        else:
            self._attrs['temperature'] = None

        self._local_tz = pytz.timezone(self._attrs['timezone'])

    async def update(self, force=False):
        """Poll API for changes to camera properties."""
        _LOGGER.debug('Updating properties for camera %s', self.name)

        if force is True or datetime.utcnow() >= self._next_update_time:
            url = '%s/%s' % (ACCESSORIES_ENDPOINT, self.id)
            camera = await self._logi._fetch(
                url=url, method='GET')

            self._set_attributes(camera)
            self._next_update_time = datetime.utcnow(
            ) + timedelta(seconds=UPDATE_REQUEST_THROTTLE)
        else:
            _LOGGER.debug('Request to update ignored, requested too soon after previous update. Throttle interval is %s.',
                          UPDATE_REQUEST_THROTTLE)

    def supported_features(self):
        """Returns an array of supported sensors for this camera."""
        return FEATURES[self.mount]

    def supports_feature(self, feature):
        """Returns a bool indicating whether a given sensor is implemented for this camera."""
        return True if feature in self.supported_features() else False

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
    def live_stream(self):
        """Return LiveStream object."""
        return LiveStream(self, self._logi)

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

    @requires_ffmpeg
    async def record_livestream(self, filename, duration):
        """Downloads the live stream into a specific file for a specific duration"""
        live_stream = self.live_stream

        # Unfortunately, the Logi API does not correctly report the segment length.
        # Worse still, segments lengths can fluctuate between requests.
        # We need to check the duration of the file each iteration and abort
        # the loop once the desired duration is reached.
        downloaded_duration = 0
        max_duration = duration.total_seconds() * 1000
        failed_segment_requests = 0
        while downloaded_duration < max_duration:
            # Bail out of the loop if too many segments fail
            if failed_segment_requests > 3:
                raise RuntimeError(
                    'Live stream video length could not be evaluated after 3 attempts.')

            await live_stream.get_segment(filename=filename, append=True)
            try:
                file_duration = _get_file_duration(filename)
                downloaded_duration = file_duration
                _LOGGER.debug('Downloaded %sms of %sms of live stream to %s.',
                              file_duration, max_duration, filename)
            except (CalledProcessError, ValueError):
                # Stream may not be ready yet.
                _LOGGER.warning(
                    'Could not evaluate length of live stream segment.')
                failed_segment_requests += 1

        # Truncate video to match desired duration
        temp_file = '%s.tmp' % (filename)
        _LOGGER.debug('Trimming trailing %sms from video, using %s as temp file.',
                      downloaded_duration - max_duration, temp_file)
        try:
            _truncate_video(filename, temp_file, duration.total_seconds())
            os.remove(filename)
            os.rename(temp_file, filename)
        except OSError:
            _delete_quietly(temp_file)
            raise

    @property
    def snapshot_url(self):
        """Returns the URL that provides a near realtime JPEG snapshot of what the camera sees."""
        url = '%s://%s/api%s/%s%s' % (PROTOCOL, self.node_id,
                                      ACCESSORIES_ENDPOINT, self.id, IMAGES_ENDPOINT)
        return url

    async def get_snapshot_image(self, filename=None):
        """Downloads a near realtime JPEG snapshot for this camera."""

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

    @requires_ffmpeg
    async def get_livestream_image(self, filename=None):
        """Downloads a realtime JPEG snapshot for this camera, generated from the camera's livestream."""

        live_stream = self.live_stream

        # Get an empty temp file to store our live stream segment
        segment_temp_file = NamedTemporaryFile(delete=False)
        segment_temp_file.close()
        segment_temp_file_path = segment_temp_file.name

        image = None

        try:
            # Download first segment from livestream
            await live_stream.get_segment(filename=segment_temp_file_path)

            # Get JPEG from FFMPEG
            image = _get_first_frame_from_video(segment_temp_file_path)

            # Delete temp file
            os.remove(segment_temp_file_path)
        except (CalledProcessError, ValueError):
            _delete_quietly(segment_temp_file_path)
            raise

        if filename:
            _write_to_file(data=image, filename=filename)
        else:
            return image

    async def set_streaming_mode(self, status):
        """Sets streaming mode for this camera."""
        if not isinstance(status, bool):
            raise ValueError('bool expected for status argument')
        if status is True:
            # Gen 1 cameras expect 'on', gen 2 cameras expect 'onAlert'
            if self.model == MODEL_GEN_1:
                await self._set_config(prop='streamingMode', internal_prop='streaming_mode',
                                       value='on', internal_value=True, value_type=str)
            else:
                await self._set_config(prop='streamingMode', internal_prop='streaming_mode',
                                       value='onAlert', internal_value=True, value_type=str)
        else:
            await self._set_config(prop='streamingMode', internal_prop='streaming_mode',
                                   value='off', internal_value=False, value_type=str)

    async def set_microphone(self, status=None, gain=None):
        """Sets microphone status and/or gain."""
        if status is not None:
            await self._set_config(prop='microphoneOn', internal_prop='microphone_on',
                                   value=status, value_type=bool)
        if gain is not None:
            await self._set_config(prop='microphoneGain', internal_prop='microphone_gain',
                                   value=gain, value_type=int)

    async def set_speaker(self, status=None, volume=None):
        """Sets speaker status and/or volume."""
        if status is not None:
            await self._set_config(prop='speakerOn', internal_prop='speaker_on', value=status, value_type=bool)
        if volume is not None:
            await self._set_config(prop='speakerVolume', internal_prop='speaker_volume', value=volume, value_type=int)

    async def set_led(self, status):
        """Sets LED on or off."""
        await self._set_config(prop='ledEnabled', internal_prop='led', value=status, value_type=bool)

    async def set_privacy_mode(self, status):
        """Sets privacy mode on or off."""
        await self._set_config(prop='privacyMode', internal_prop='privacy_mode', value=status, value_type=bool)

    async def set_battery_saving_mode(self, status):
        """Sets the battery saving mode on or off."""
        await self._set_config(prop='saveBattery', internal_prop='battery_saving', value=status, value_type=bool)

    async def _set_config(self, prop, internal_prop, value, value_type, internal_value=None):
        """Internal method for updating the camera's configuration."""
        if not isinstance(value, value_type):
            raise ValueError('%s expected for status argument' % (value_type))

        url = '%s/%s' % (ACCESSORIES_ENDPOINT, self.id)
        payload = {prop: value}

        _LOGGER.debug('Setting %s to %s', prop, str(value))

        try:
            req = await self._logi._fetch(
                url=url, method='PUT', request_body=payload, raw=True)
            req.close()

            # Update camera props to reflect change
            self._attrs[internal_prop] = internal_value if internal_value is not None else value
            _LOGGER.debug('Successfully set %s to %s', prop,
                          str(value))
        except ClientResponseError as error:
            _LOGGER.error(
                'Status code %s returned when updating %s to %s', error.code, prop, str(value))
            raise

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
    def streaming_mode(self):
        """Return streaming mode for camera (soft "on")."""
        return self._attrs.get('streaming_mode')

    @property
    def battery_level(self):
        """Return battery level (integer between 0-100)."""
        battery_level = self._attrs.get('battery_level')
        try:
            return int(battery_level)
        except ValueError:
            return battery_level

    @property
    def battery_saving(self):
        """Return whether battery saving mode is activated."""
        return self._attrs.get('battery_saving')

    @property
    def is_charging(self):
        """Return bool indicating whether the device is currently connected to power."""
        return self._attrs.get('is_charging')

    @property
    def model(self):
        """Return model number."""
        return self._attrs.get('model')

    @property
    def model_generation(self):
        """Return product type, derived from other camera properties."""
        if self.model == MODEL_GEN_1:
            return MODEL_GEN_1_NAME
        if self.model == MODEL_GEN_2:
            return MODEL_GEN_2_NAME
        return MODEL_GEN_UNKNOWN_NAME

    @property
    def mount(self):
        """Returns the camera mount type."""
        if self.model == MODEL_GEN_1:
            return MODEL_GEN_1_MOUNT
        if self.model == MODEL_GEN_2:
            if isinstance(self.battery_level, int):
                if self.battery_level < 0:
                    return MODEL_GEN_2_MOUNT_WIRED
                return MODEL_GEN_2_MOUNT_WIRELESS
            return MODEL_GEN_2_MOUNT_WIRED
        return MODEL_GEN_UNKNOWN_NAME

    @property
    def firmware(self):
        """Return firmware version."""
        return self._attrs.get('firmware')

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

    @property
    def ip_address(self):
        """Return local IP address for camera."""
        return self._attrs.get('ip_address')

    @property
    def mac_address(self):
        """Return MAC address for camera's WiFi interface."""
        return self._attrs.get('mac_address')

    @property
    def wifi_ssid(self):
        """Return WiFi SSID name the camera last connected with."""
        return self._attrs.get('wifi_ssid')

    @property
    def microphone_on(self):
        """Return bool indicating whether microphone is enabled."""
        return self._attrs.get('microphone_on')

    @property
    def microphone_gain(self):
        """Return microphone gain using absolute scale (1-100)."""
        gain = self._attrs.get('microphone_gain')
        try:
            return int(gain)
        except ValueError:
            return gain

    @property
    def speaker_on(self):
        """Return bool indicating whether speaker is currently enabled."""
        return self._attrs.get('speaker_on')

    @property
    def speaker_volume(self):
        """Return speaker volume using absolute scale (1-100)."""
        volume = self._attrs.get('speaker_volume')
        try:
            return int(volume)
        except ValueError:
            return volume

    @property
    def led_on(self):
        """Return bool indicating whether LED is enabled."""
        return self._attrs.get('led')

    @property
    def privacy_mode(self):
        """Return bool indicating whether privacy mode is enabled (ie. no activities recorded)."""
        return self._attrs.get('privacy_mode')

    @property
    def plan_name(self):
        """Return plan/subscription product assigned to camera (free tier, paid tier, etc)."""
        return self._attrs.get('plan_name')
