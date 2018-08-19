"""Helper functions for Logi Circle API unit tests"""
import os


def get_fixture_name(filename):
    """Strips .json from filename when building fixtures dict key"""
    return filename.replace('.json', '')


def get_fixtures():
    """Grabs all fixtures and returns them in a dict"""
    fixtures = {}
    path = os.path.join(os.path.dirname(__file__), 'fixtures')
    for filename in os.listdir(path):
        if filename.endswith(".json"):
            with open(os.path.join(path, filename)) as fdp:
                fixture = fdp.read()
                fixtures[get_fixture_name(filename)] = fixture
            continue
        else:
            continue
    return fixtures
