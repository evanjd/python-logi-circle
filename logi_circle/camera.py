"""Camera class, representing a Logi Circle device"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import pytz
from .const import (ACCESSORIES_ENDPOINT,
                    LIVE_IMAGE_ENDPOINT,
                    ACCEPT_IMAGE_HEADER,
                    DEFAULT_IMAGE_QUALITY,
                    DEFAULT_IMAGE_REFRESH)
from .utils import _stream_to_file

_LOGGER = logging.getLogger(__name__)


class Camera():
    """Generic implementation for Logi Circle camera."""

    def __init__(self, logi, camera):
        """Initialise Logi Camera object."""
        self.logi = logi
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
        except (KeyError, TypeError):
            _LOGGER.error(
                'Camera could not be initialised, API did not return one or more required properties.')
            raise

        # Optional attributes
        self._attrs['model'] = camera.get('modelNumber', 'Unknown')
        self._attrs['mac_address'] = camera.get('mac', None)
        self._attrs['streaming_enabled'] = config.get('streamingEnabled', False)
        self._attrs['timezone'] = config.get('timeZone', 'UTC')
        self._attrs['battery_level'] = config.get('batteryLevel', None)
        self._attrs['is_charging'] = config.get('batteryCharging', None)
        self._attrs['battery_saving'] = config.get('saveBattery', None)
        self._attrs['signal_strength_percentage'] = config.get(
            'wifiSignalStrength', None)
        self._attrs['firmware'] = config.get('firmwareVersion', None)
        self._attrs['microphone_on'] = config.get('microphoneOn', False)
        self._attrs['microphone_gain'] = config.get('microphoneGain', None)
        self._attrs['speaker_on'] = config.get('speakerOn', False)
        self._attrs['speaker_volume'] = config.get('speakerVolume', None)
        self._attrs['led_on'] = config.get('ledEnabled', False)
        self._attrs['privacy_mode'] = config.get('privacyMode', False)

        self._local_tz = pytz.timezone(self._attrs['timezone'])

    async def get_image(self,
                        quality=DEFAULT_IMAGE_QUALITY,
                        refresh=DEFAULT_IMAGE_REFRESH,
                        filename=None):
        """Download the most recent snapshot image for this camera"""

        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.id, LIVE_IMAGE_ENDPOINT)
        accept_header = ACCEPT_IMAGE_HEADER
        params = {'quality': quality, 'refresh': str(refresh).lower()}

        image = await self.logi._fetch(url=url, raw=True, headers=accept_header, params=params)
        if filename:
            await _stream_to_file(image.content, filename)
            image.close()
            return True
        content = await image.read()
        image.close()
        return content

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
        """Return bool indicating whether device is online and can accept commands (hard "on")."""
        return self._attrs.get('is_connected')

    @property
    def streaming_enabled(self):
        """Return streaming mode for camera (soft "on")."""
        return self._attrs.get('streaming_enabled')

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
    def is_charging(self):
        """Return bool indicating whether the device is currently connected to power."""
        return self._attrs.get('is_charging')

    @property
    def model(self):
        """Return model number."""
        return self._attrs.get('model')

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
    def microphone_on(self):
        """Return bool indicating whether microphone is enabled."""
        return self._attrs.get('microphone_on')

    @property
    def microphone_gain(self):
        """Return microphone gain using absolute scale (1-100)."""
        return self._attrs.get('microphone_gain')

    @property
    def speaker_on(self):
        """Return bool indicating whether speaker is currently enabled."""
        return self._attrs.get('speaker_on')

    @property
    def speaker_volume(self):
        """Return speaker volume using absolute scale (1-100)."""
        return self._attrs.get('speaker_volume')

    @property
    def led_on(self):
        """Return bool indicating whether LED is enabled."""
        return self._attrs.get('led_on')

    @property
    def privacy_mode(self):
        """Return bool indicating whether privacy mode is enabled (ie. no activities recorded)."""
        return self._attrs.get('privacy_mode')
