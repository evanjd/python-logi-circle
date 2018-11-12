"""Camera class, representing a Logi Circle device"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import pytz

_LOGGER = logging.getLogger(__name__)


class Camera():
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
        self._attrs['model'] = camera.get('modelNumber', 'Unknown')
        self._attrs['mac_address'] = camera.get('mac', None)
        self._attrs['streaming_enabled'] = config.get('streamingEnabled', False)
        self._attrs['timezone'] = config.get('timeZone', 'UTC')
        self._attrs['battery_level'] = config.get('batteryLevel', None)
        self._attrs['is_charging'] = config.get('batteryCharging', None)
        self._attrs['battery_saving'] = config.get('saveBattery', None)
        self._attrs['wifi_signal_strength'] = config.get(
            'wifiSignalStrength', None)
        self._attrs['firmware'] = config.get('firmwareVersion', None)
        self._attrs['microphone_on'] = config.get('microphoneOn', False)
        self._attrs['microphone_gain'] = config.get('microphoneGain', None)
        self._attrs['speaker_on'] = config.get('speakerOn', False)
        self._attrs['speaker_volume'] = config.get('speakerVolume', None)
        self._attrs['led'] = config.get('ledEnabled', False)
        self._attrs['privacy_mode'] = config.get('privacyMode', False)

        self._local_tz = pytz.timezone(self._attrs['timezone'])

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
