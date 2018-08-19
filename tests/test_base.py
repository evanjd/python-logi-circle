"""Register Logi API with mock aiohttp ClientSession and responses."""
import os
import unittest
import asyncio
from tests.helpers import get_fixtures

USERNAME = 'test@email.com'
PASSWORD = 'correct_horse_battery_staple'
CACHE = os.path.join(os.path.dirname(__file__), 'cache.db')
FIXTURES = get_fixtures()


class LogiUnitTestBase(unittest.TestCase):
    """Base Logi Circle test class."""

    def setUp(self):
        """Setup unit test and load mock."""
        from logi_circle import Logi

        self.logi = Logi(USERNAME, PASSWORD, cache_file=CACHE)
        self.logi_no_reuse = \
            Logi(USERNAME, PASSWORD, reuse_session=False)

        self.username = USERNAME
        self.password = PASSWORD
        self.cache = CACHE
        self.fixtures = FIXTURES

        self.loop = asyncio.new_event_loop()

    def cleanup(self):
        """Cleanup any data created from the tests."""
        self.loop.close()
        print('closing loop')
        self.logi = None
        self.logi_no_reuse = None
        if os.path.isfile(CACHE):
            os.remove(CACHE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()
