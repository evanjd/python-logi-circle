"""The tests utils.py for the Logi Circle platform."""
import os
import sys
import unittest
from unittest.mock import MagicMock
import asyncio
from logi_circle.utils import (
    _get_session_cookie, _handle_response, _clean_cache, _exists_cache, _save_cache, _read_cache,
    _delete_quietly)
from logi_circle.const import (CACHE_ATTRS, COOKIE_NAME)
from logi_circle.exception import BadSession

CACHE = 'tests/cache.db'
FAKE = 'tests/fake.db'
DATA = {'key': 'value'}


class FakeCookie():
    """Mock Cookie object"""

    def __init__(self, cookie_name):
        """Initialise fake cookie object."""
        self.key = cookie_name


class FakeRequest():
    """Mock Request object"""

    def __init__(self, status):
        """Initialise fake request object."""
        self.status = status
        self.closed = False

    @staticmethod
    async def json():
        """Mock json() method from aiohttp request"""
        return {}

    def close(self):
        """Mock close() method from aiohttp request"""
        self.closed = True

    def raise_for_status(self):
        """Mock raise_for_status() method from aiohttp request"""
        if self.status >= 300:
            raise Exception('Mock exception')


class TestUtils(unittest.TestCase):
    """Test utils.py."""

    def cleanup(self):
        """Cleanup any data created from the tests."""
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()

    def test_get_session_cookie(self):
        """Test _get_session_cookie method"""
        mock_cookie_jar = [
            FakeCookie('not_the_cookie'),
            FakeCookie(COOKIE_NAME)
        ]
        self.assertEqual(_get_session_cookie(mock_cookie_jar).key, COOKIE_NAME)

        invalid_cookie_jar = [
            FakeCookie('not_the_cookie')
        ]
        with self.assertRaises(BadSession):
            _get_session_cookie(invalid_cookie_jar)

    def test_handle_response(self):
        """Test _handle_response method"""

        async def run_test():
            with self.assertRaises(BadSession):
                await _handle_response(FakeRequest(401), raw=False)
            with self.assertRaises(Exception):
                await _handle_response(FakeRequest(500), raw=False)

            req1 = await _handle_response(FakeRequest(200), raw=False)
            self.assertIsInstance(req1, dict)

            req2 = await _handle_response(FakeRequest(200), raw=True)
            self.assertIsInstance(req2, FakeRequest)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())
        loop.close()

    def test_init_clean_cache(self):
        """Test _clean_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_clean_cache(CACHE), dict)
        self.cleanup()

    def test_exists_cache(self):
        """Test _exists_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertTrue(_exists_cache(CACHE))
        self.cleanup()

    def test_read_cache(self):
        """Test _read_cache method."""
        self.assertTrue(_save_cache(DATA, CACHE))
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_delete_quietly(self):
        """Test _delete_quietly method."""
        # Save original os.remove method
        os_remove = os.remove

        # Test successful deletion
        os.remove = MagicMock()
        _delete_quietly('/tmp/existing_file.txt')
        os.remove.assert_called_once()

        # Test unsuccessful deletion (should not raise exception)
        os.remove = MagicMock(side_effect=OSError)
        _delete_quietly('/tmp/missing_file.txt')
        os.remove.assert_called_once()

        # Restore original os.remove method
        os.remove = os_remove

    def test_read_cache_eoferror(self):
        """Test _read_cache method."""
        open(CACHE, 'a').close()
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_read_cache_dict(self):
        """Test _read_cache with expected dict."""
        self.assertTrue(_save_cache(CACHE_ATTRS, CACHE))
        self.assertIsInstance(_read_cache(CACHE), dict)
        self.cleanup()

    def test_general_exceptions(self):
        """Test exception triggers on utils.py"""
        self.assertRaises(TypeError, _clean_cache, True)
        if sys.version_info.major == 2:
            self.assertRaises(TypeError, _read_cache, True)
        else:
            self.assertRaises(OSError, _read_cache, True)
