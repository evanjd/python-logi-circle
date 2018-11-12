"""Register Logi API with mock aiohttp ClientSession and responses."""
import os
import unittest
import asyncio
from tests.helpers import get_fixtures

CLIENT_ID = 'abcdefghijklmnopqrstuvwxyz'
CLIENT_SECRET = 'correct_horse_battery_staple'
REDIRECT_URI = 'https://my.groovy.app/'
API_KEY = 'ZYXWVUTSRQPONMLKJIHGFEDCBA'
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cache.db')
FIXTURES = get_fixtures()


class LogiUnitTestBase(unittest.TestCase):
    """Base Logi Circle test class."""

    def setUp(self):
        """Setup unit test, create event loop."""
        from logi_circle import LogiCircle

        self.logi = LogiCircle(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               redirect_uri=REDIRECT_URI,
                               cache_file=CACHE_FILE,
                               api_key=API_KEY)
        self.fixtures = FIXTURES
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.redirect_uri = REDIRECT_URI
        self.cache_file = CACHE_FILE

        self.loop = asyncio.new_event_loop()

    def cleanup(self):
        """Cleanup any data created from the tests."""
        self.loop.close()
        self.logi = None
        if os.path.isfile(CACHE_FILE):
            os.remove(CACHE_FILE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()
