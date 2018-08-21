# -*- coding: utf-8 -*-
"""Tests for the Logi API Camera class."""
from datetime import datetime
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT, ACTIVITIES_ENDPOINT, ACCESSORIES_ENDPOINT
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
                self.assertTrue(
                    camera.is_streaming, 'Camera is_streaming mismatch')
                self.assertFalse(
                    camera.is_charging, 'Camera is_charging mismatch')
                self.assertEqual(
                    camera.battery_level, 95, 'Battery level mismatch')
                self.assertEqual(
                    camera.model, 'A1234', 'Model mismatch')
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

    def test_power_method(self):
        """Test enabling and disabling of power status"""
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
                self.assertTrue(
                    camera.is_streaming, 'Camera is_streaming mismatch')
                # Disable streaming
                await camera.set_streaming_mode(False)
                # Streaming mode is off
                self.assertFalse(camera.is_streaming,
                                 'Camera streaming is on after turning off')
                # Enable streaming
                await camera.set_streaming_mode(True)
                # Streaming mode is on
                self.assertTrue(camera.is_streaming,
                                'Camera streaming is off after turning on')

        self.loop.run_until_complete(run_test())
