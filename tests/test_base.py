"""Register Logi API with mock aiohttp ClientSession and responses."""
import os
import pickle
import json
import unittest
import asyncio
from tests.helpers import get_fixtures
from logi_circle.const import DEFAULT_SCOPES
from logi_circle.auth import AuthProvider

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

    def get_authorized_auth_provider(self):
        """Returns a pre-authorized AuthProvider instance"""
        auth_fixture = json.loads(self.fixtures['auth_code'])
        token = {}
        token[self.client_id] = auth_fixture
        with open(self.cache_file, 'wb') as pickle_db:
            pickle.dump(token, pickle_db)

        return AuthProvider(client_id=self.client_id,
                            client_secret=self.client_secret,
                            redirect_uri=self.redirect_uri,
                            scopes=DEFAULT_SCOPES,
                            cache_file=self.cache_file,
                            logi_base=self.logi)

    def cleanup(self):
        """Cleanup any data created from the tests."""
        async def close_session():
            await self.logi.close()

        self.loop.run_until_complete(close_session())

        self.loop.close()
        self.logi = None
        if os.path.isfile(CACHE_FILE):
            os.remove(CACHE_FILE)

    def tearDown(self):
        """Stop everything started."""
        self.cleanup()
