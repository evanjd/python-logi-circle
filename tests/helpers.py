"""Helper functions for Logi Circle API unit tests."""
import os
import asyncio


def get_fixture_name(filename):
    """Strips extension from filename when building fixtures dict key."""
    return os.path.splitext(filename)[0]


def get_fixtures():
    """Grabs all fixtures and returns them in a dict."""
    fixtures = {}
    path = os.path.join(os.path.dirname(__file__), 'fixtures')
    for filename in os.listdir(path):
        with open(os.path.join(path, filename)) as fdp:
            fixture = fdp.read()
            fixtures[get_fixture_name(filename)] = fixture
            continue
    return fixtures


def async_return(result):
    """Mock a return from an async function."""
    future = asyncio.Future()
    future.set_result(result)
    return future


class FakeStream():

    async def read(self):
        return b'123'

    def close(self):
        return True
