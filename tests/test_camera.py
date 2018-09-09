# -*- coding: utf-8 -*-
"""Tests for the Logi API Camera class."""
from datetime import datetime
from unittest.mock import MagicMock
import aresponses
from tests.test_base import LogiUnitTestBase
from tests.helpers import async_return
from logi_circle.const import (API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT, ACTIVITIES_ENDPOINT,
                               ACCESSORIES_ENDPOINT, FEATURES, MODEL_GEN_1_MOUNT, MODEL_GEN_2_MOUNT_WIRED,
                               MODEL_GEN_2_MOUNT_WIRELESS)
from logi_circle.activity import Activity


class TestCamera(LogiUnitTestBase):
    """Unit test for the Camera class."""

    def test_camera_props(self):
        """Test camera properties match fixture"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]

                # Has the ID we expect
                self.assertEqual(camera.id, 'mock-camera', 'ID mismatch')

                # All other properties as expected
                self.assertEqual(
                    camera.name, 'Mock Camera', 'Name mismatch')
                self.assertTrue(
                    camera.is_connected, 'Camera is_connected mismatch')
                self.assertEqual(camera.streaming_mode, True,
                                 'Camera streaming_mode mismatch')
                self.assertFalse(
                    camera.is_charging, 'Camera is_charging mismatch')
                self.assertEqual(
                    camera.battery_level, 95, 'Battery level mismatch')
                self.assertEqual(
                    camera.model, 'A1533', 'Model mismatch')
                self.assertEqual(
                    camera.model_generation, '1st generation', 'Model generation mismatch')
                self.assertEqual(
                    camera.mount, 'Charging ring', 'Mount mismatch')
                self.assertEqual(
                    camera.node_id, 'node-mocked.video.logi.com', 'Node ID mismatch')
                self.assertEqual(
                    camera.firmware, '999.9.999', 'Firmware mismatch')
                self.assertEqual(
                    camera.timezone, 'Australia/Sydney', 'Timezone mismatch')
                self.assertEqual(
                    camera.signal_strength_percentage, 99, 'Signal strength mismatch')
                self.assertEqual(
                    camera.signal_strength_category, 'Excellent', 'Signal strength category mismatch')
                self.assertEqual(
                    camera.temperature, 20, 'Temperature mismatch')
                self.assertEqual(
                    camera.humidity, 50, 'Humidity mismatch')
                self.assertEqual(
                    camera.ip_address, '127.0.0.1', 'IP address mismatch')
                self.assertEqual(
                    camera.mac_address, '00:00:00:00:00:00', 'MAC address mismatch')
                self.assertEqual(
                    camera.wifi_ssid, 'Mock LAN', 'WiFi SSID mismatch')
                self.assertEqual(
                    camera.microphone_on, True, 'Microphone status mismatch')
                self.assertEqual(
                    camera.microphone_gain, 100, 'Microphone gain mismatch')
                self.assertEqual(
                    camera.speaker_on, True, 'Speaker status mismatch')
                self.assertEqual(
                    camera.speaker_volume, 90, 'Speaker volume mismatch')
                self.assertEqual(
                    camera.led_on, False, 'LED status mismatch')
                self.assertEqual(
                    camera.privacy_mode, False, 'Privacy mode mismatch')
                self.assertEqual(
                    camera.plan_name, 'Mock Plan', 'Plan name mismatch')

        self.loop.run_until_complete(run_test())

    def test_camera_update(self):
        """Test camera properties change when updating from server"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT + '/mock-camera', 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessory'],
                                              headers={'content-type': 'application/json'}))

                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]

                # Test properties before update
                self.assertEqual(
                    camera.node_id, 'node-mocked.video.logi.com', 'Node ID mismatch')
                self.assertEqual(
                    camera.signal_strength_percentage, 99, 'Signal strength mismatch')
                self.assertEqual(
                    camera.signal_strength_category, 'Excellent', 'Signal strength category mismatch')
                self.assertEqual(
                    camera.battery_level, 95, 'Battery level mismatch')

                # Perform update
                await camera.update()

                # Test properties changed after update
                self.assertEqual(
                    camera.node_id, 'node-mocked-2.video.logi.com', 'Node ID mismatch after update')
                self.assertEqual(
                    camera.signal_strength_percentage, 79, 'Signal strength mismatch after update')
                self.assertEqual(
                    camera.signal_strength_category, 'Good', 'Signal strength category mismatch after update')
                self.assertEqual(
                    camera.battery_level, 90, 'Battery level mismatch after update')

        self.loop.run_until_complete(run_test())

    def test_gen2_props(self):
        """Test 2nd gen camera properties match fixture"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories_gen2'],
                                              headers={'content-type': 'application/json'}))
                # Perform implicit login, and get camera
                cameras = await logi.cameras
                camera_wired = cameras[0]
                camera_wireless = cameras[1]

                # Test wired camera props
                self.assertEqual(
                    camera_wired.id, 'mock-camera-wired', 'ID mismatch')
                self.assertEqual(camera_wired.mount, 'Wired', 'Mount mismatch')
                self.assertEqual(
                    camera_wired.model_generation, '2nd generation')
                self.assertEqual(
                    camera_wired.battery_level, -1, 'Battery level mismatch')

                # Test wireless camera props
                self.assertEqual(camera_wireless.id,
                                 'mock-camera-wireless', 'ID mismatch')
                self.assertEqual(camera_wireless.mount,
                                 'Wireless', 'Mount mismatch')
                self.assertEqual(
                    camera_wireless.model_generation, '2nd generation')
                self.assertEqual(
                    camera_wireless.battery_level, 63, 'Battery level mismatch')

        self.loop.run_until_complete(run_test())

    def test_last_activity(self):
        """Test retrieval of last camera activity"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT + '/mock-camera' + ACTIVITIES_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=self.fixtures['activities_1'],
                                              headers={'content-type': 'application/json'}))

                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]
                # Get activity
                last_activity = await camera.last_activity
                self.assertIsInstance(last_activity, Activity)

        self.loop.run_until_complete(run_test())

    def test_get_activity_history(self):
        """Test retrieval of camera activity history"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT + '/mock-camera' + ACTIVITIES_ENDPOINT, 'post',
                          aresponses.Response(status=200,
                                              text=self.fixtures['activities_5'],
                                              headers={'content-type': 'application/json'}))

                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]
                # Get activity history
                activities = await camera.query_activity_history(date_filter=datetime.now(),
                                                                 date_operator='<',
                                                                 property_filter='playbackDuration > 0',
                                                                 limit=5)
                self.assertEqual(len(activities), 5)
                for activity in activities:
                    self.assertIsInstance(activity, Activity)

        self.loop.run_until_complete(run_test())

    def test_feature_mapping(self):
        """Test correct features returned per camera mount"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories_gen2'],
                                              headers={'content-type': 'application/json'}))

                # Get gen 1 camera
                camera = (await logi.cameras)[0]

                gen_1_features = FEATURES[MODEL_GEN_1_MOUNT]
                for feature in gen_1_features:
                    self.assertTrue(camera.supports_feature(
                        feature), 'Feature mapping mismatch')
                self.assertFalse(camera.supports_feature(
                    'orbital_laser'), 'Feature mapping mismatch')

                # Get gen 2 cameras
                cameras = await logi.cameras
                camera_wired = cameras[0]
                camera_wireless = cameras[1]

                gen_2_wired_features = FEATURES[MODEL_GEN_2_MOUNT_WIRED]
                for feature in gen_2_wired_features:
                    self.assertTrue(camera_wired.supports_feature(
                        feature), 'Feature mapping mismatch')
                # Wired gen 2 cameras have no battery, so battery_level should be false
                self.assertFalse(camera_wired.supports_feature(
                    'battery_level'), 'Feature mapping mismatch')

                gen_2_wireless_features = FEATURES[MODEL_GEN_2_MOUNT_WIRELESS]
                for feature in gen_2_wireless_features:
                    self.assertTrue(camera_wireless.supports_feature(
                        feature), 'Feature mapping mismatch')
                self.assertTrue(camera_wireless.supports_feature(
                    'battery_level'), 'Feature mapping mismatch')

        self.loop.run_until_complete(run_test())

    def test_set_streaming_mode(self):
        """Test enabling and disabling of streaming mode"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + ACCESSORIES_ENDPOINT + '/mock-camera', 'put',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + ACCESSORIES_ENDPOINT + '/mock-camera', 'put',
                          aresponses.Response(status=200))

                # Perform implicit login, and get camera
                camera = (await logi.cameras)[0]
                # Streaming mode is on (as per fixture)
                self.assertEqual(camera.streaming_mode, True,
                                 'Camera streaming_mode mismatch')
                # Disable streaming
                await camera.set_streaming_mode(False)
                # Streaming mode is off
                self.assertEqual(camera.streaming_mode, False,
                                 'Camera streaming is on after turning off')
                # Enable streaming
                await camera.set_streaming_mode(True)
                # Streaming mode is on
                self.assertEqual(camera.streaming_mode, True,
                                 'Camera streaming is off after turning on')

        self.loop.run_until_complete(run_test())

    def test_gen_specific_streaming_modes(self):
        """Test that correct streaming mode is set per generation"""
        logi = self.logi_no_reuse

        async def run_test():
            async with aresponses.ResponsesMockServer(loop=self.loop) as arsps:
                arsps.add(API_HOST, '/api' + AUTH_ENDPOINT, 'post',
                          aresponses.Response(status=200))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories_gen2'],
                                              headers={'content-type': 'application/json'}))
                arsps.add(API_HOST, '/api' + CAMERAS_ENDPOINT, 'get',
                          aresponses.Response(status=200,
                                              text=self.fixtures['accessories'],
                                              headers={'content-type': 'application/json'}))

                # Get gen 2 cameras - 'onAlert' for on, 'off' for off
                cameras = await logi.cameras
                camera_wired = cameras[0]
                camera_wireless = cameras[1]

                camera_wired._set_config = MagicMock(
                    return_value=async_return(True))
                camera_wireless._set_config = MagicMock(
                    return_value=async_return(True))

                await camera_wired.set_streaming_mode(True)
                await camera_wireless.set_streaming_mode(True)

                camera_wired._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=True,
                    prop='streamingMode', value='onAlert', value_type=str)
                camera_wireless._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=True,
                    prop='streamingMode', value='onAlert', value_type=str)

                await camera_wired.set_streaming_mode(False)
                await camera_wireless.set_streaming_mode(False)

                camera_wired._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=False,
                    prop='streamingMode', value='off', value_type=str)
                camera_wireless._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=False,
                    prop='streamingMode', value='off', value_type=str)

                # Get gen 1 camera, 'on' for on, 'off' for off
                cameras = await logi.cameras
                camera_gen1 = cameras[0]

                camera_gen1._set_config = MagicMock(
                    return_value=async_return(True))

                await camera_gen1.set_streaming_mode(True)

                camera_gen1._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=True,
                    prop='streamingMode', value='on', value_type=str)

                await camera_gen1.set_streaming_mode(False)

                camera_gen1._set_config.assert_called_with(
                    internal_prop='streaming_mode', internal_value=False,
                    prop='streamingMode', value='off', value_type=str)

        self.loop.run_until_complete(run_test())
