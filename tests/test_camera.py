# -*- coding: utf-8 -*-
"""The tests for the Logi API platform."""
import json
from urllib.parse import urlparse, parse_qs
import pickle
import aresponses
import aiohttp
from tests.test_base import LogiUnitTestBase
from logi_circle.camera import Camera


class TestCamera(LogiUnitTestBase):
    """Unit test for core Logi class."""

    def test_camera_props(self):
        """Camera props should match fixtures"""
        gen1_fixture = json.loads(self.fixtures['accessories'])[0]
        test_camera = Camera(self.logi, gen1_fixture)

        # Mandatory props
        self.assertEqual(test_camera.id, gen1_fixture['accessoryId'])
        self.assertEqual(test_camera.name, gen1_fixture['name'])
        self.assertEqual(test_camera.is_connected, gen1_fixture['isConnected'])
        gen1_fixture['cfg'] = gen1_fixture['configuration']

        # Optional props
        self.assertEqual(test_camera.model, gen1_fixture['modelNumber'])
        self.assertEqual(test_camera.mac_address, gen1_fixture['mac'])
        self.assertEqual(test_camera.streaming_enabled, gen1_fixture['cfg']['streamingEnabled'])
        self.assertEqual(test_camera.timezone, gen1_fixture['cfg']['timeZone'])
        self.assertEqual(test_camera.battery_level, gen1_fixture['cfg']['batteryLevel'])
        self.assertEqual(test_camera.is_charging, gen1_fixture['cfg']['batteryCharging'])
        self.assertEqual(test_camera.battery_saving, gen1_fixture['cfg']['saveBattery'])
        self.assertEqual(test_camera.signal_strength_percentage, gen1_fixture['cfg']['wifiSignalStrength'])
        self.assertEqual(test_camera.firmware, gen1_fixture['cfg']['firmwareVersion'])
        self.assertEqual(test_camera.microphone_on, gen1_fixture['cfg']['microphoneOn'])
        self.assertEqual(test_camera.microphone_gain, gen1_fixture['cfg']['microphoneGain'])
        self.assertEqual(test_camera.speaker_on, gen1_fixture['cfg']['speakerOn'])
        self.assertEqual(test_camera.speaker_volume, gen1_fixture['cfg']['speakerVolume'])
        self.assertEqual(test_camera.led_on, gen1_fixture['cfg']['ledEnabled'])
        self.assertEqual(test_camera.privacy_mode, gen1_fixture['cfg']['privacyMode'])

    def test_missing_mandatory_props(self):
        """Camera should raise if mandatory props missing"""
        incomplete_camera = {
            "name": "Incomplete cam",
            "accessoryId": "123",
            "configuration": {
                "stuff": "123"
            }
            # Missing isConnected
        }

        with self.assertRaises(KeyError):
            Camera(self.logi, incomplete_camera)

    def test_missing_optional_props(self):
        """Camera should not raise if optional props missing"""
        incomplete_camera = {
            "name": "Incomplete cam",
            "accessoryId": "123",
            "configuration": {
                "modelNumber": "1234",
                "batteryLevel": 1
                # Lots of missing optional cfg props
            },
            "isConnected": False
        }

        camera = Camera(self.logi, incomplete_camera)
        self.assertEqual(camera.name, "Incomplete cam")
        self.assertEqual(camera.id, "123")
        self.assertEqual(camera.is_connected, False)

        # Optional int/string props not passed to Camera should be None
        self.assertIsNone(camera.mac_address)
        self.assertIsNone(camera.is_charging)
        self.assertIsNone(camera.battery_saving)
        self.assertIsNone(camera.signal_strength_percentage)
        self.assertIsNone(camera.signal_strength_category)
        self.assertIsNone(camera.firmware)
        self.assertIsNone(camera.microphone_gain)
        self.assertIsNone(camera.speaker_volume)

        # Optional bools should be neutral (false)
        self.assertFalse(camera.streaming_enabled)
        self.assertFalse(camera.microphone_on)
        self.assertFalse(camera.speaker_on)
        self.assertFalse(camera.led_on)
        self.assertFalse(camera.privacy_mode)

        # Timezone should fallback to UTC
        self.assertEqual(camera.timezone, "UTC")
