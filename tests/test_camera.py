# -*- coding: utf-8 -*-
"""Tests for the Logi API Camera class."""
import aresponses
from tests.test_base import LogiUnitTestBase
from logi_circle.const import API_HOST, AUTH_ENDPOINT, CAMERAS_ENDPOINT


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
                    camera.timezone, 'Australia/Sydney', 'Timezone mismatch')
                self.assertEqual(
                    camera.signal_strength_percentage, 99, 'Signal strength mismatch')
                self.assertEqual(
                    camera.signal_strength_category, 'Excellent', 'Signal strength category mismatch')
                self.assertEqual(
                    camera.temperature, 20, 'Temperature mismatch')
                self.assertEqual(
                    camera.humidity, 50, 'Humidity mismatch')

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
