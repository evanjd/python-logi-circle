"""Register Logi API with mock aiohttp ClientSession and responses."""
import os
import unittest
import asyncio
from tests.helpers import get_fixtures

USERNAME = 'test@email.com'
PASSWORD = 'correct_horse_battery_staple'
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cache.db')
FIXTURES = get_fixtures()


class LogiUnitTestBase(unittest.TestCase):
    """Base Logi Circle test class."""

    def setUp(self):
        """Setup unit test, create event loop."""
        from logi_circle import Logi

        self.logi = Logi(USERNAME, PASSWORD, cache_file=CACHE_FILE)
        self.logi_no_reuse = \
            Logi(USERNAME, PASSWORD, reuse_session=False)

        self.username = USERNAME
        self.password = PASSWORD
        self.cache_file = CACHE_FILE
        self.fixtures = FIXTURES

        self.loop = asyncio.new_event_loop()

    def cleanup(self):
        """Cleanup any data created from the tests."""
        self.loop.close()
        self.logi = None
        self.logi_no_reuse = None
        if os.path.isfile(CACHE_FILE):
            os.remove(CACHE_FILE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()
