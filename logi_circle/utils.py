"""Utilities library shared by the Logi, Camera and Activity classes."""
# coding: utf-8
# vim:sw=4:ts=4:et:
import os
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from logi_circle.const import (
    CACHE_ATTRS, COOKIE_NAME, MODEL_GEN_1, MODEL_GEN_2, MODEL_TYPE_GEN_1,
    MODEL_TYPE_GEN_2_WIRED, MODEL_TYPE_GEN_2_WIRELESS, MODEL_TYPE_UNKNOWN)
from .exception import BadSession

_LOGGER = logging.getLogger(__name__)


def _get_session_cookie(cookie_jar):
    """Iterates through the session's AbstractCookieJar and returns the cookie relevant to Logi API sessions"""
    for cookie in cookie_jar:
        if cookie.key == COOKIE_NAME:
            return cookie
    raise BadSession()


async def _handle_response(request, raw):
    if request.status == 401:
        # Session has likely expired. Re-authentiate.
        raise BadSession()

    # Throw unhandled error if request failed for any other reason
    request.raise_for_status()

    if raw:
        return request
    else:
        resp = await request.json()
        request.close()
        return resp


async def _stream_to_file(stream, filename, open_mode='wb'):
    """Stream aiohttp response to file"""
    with open(filename, open_mode) as file_handle:
        while True:
            chunk = await stream.read(1024)
            if not chunk:
                break
            file_handle.write(chunk)


def _model_number_to_type(model, battery_level=-1):
    """Converts the model number to a friendly product name."""
    if model == MODEL_GEN_1:
        return MODEL_TYPE_GEN_1
    if model == MODEL_GEN_2:
        if battery_level < 0:
            return MODEL_TYPE_GEN_2_WIRED
        return MODEL_TYPE_GEN_2_WIRELESS
    return MODEL_TYPE_UNKNOWN


def _write_to_file(data, filename):
    """Write bytes data to file"""
    with open(filename, 'wb') as file_handle:
        file_handle.write(data)


def _clean_cache(filename):
    """Remove filename if pickle version mismatch."""
    if os.path.isfile(filename):
        os.remove(filename)

    # initialize cache since file was removed
    initial_cache_data = CACHE_ATTRS
    _save_cache(initial_cache_data, filename)
    return initial_cache_data


def _exists_cache(filename):
    """Check if filename exists and if is pickle object."""
    return bool(os.path.isfile(filename))


def _save_cache(data, filename):
    """Dump data into a pickle file."""
    with open(filename, 'wb') as pickle_db:
        pickle.dump(data, pickle_db)
    return True


def _read_cache(filename):
    """Read data from a pickle file."""
    try:
        if os.path.isfile(filename):
            data = pickle.load(open(filename, 'rb'))

            # make sure pickle obj has the expected defined keys
            # if not reinitialize cache
            if data.keys() != CACHE_ATTRS.keys():
                raise EOFError
            return data

    except (EOFError, ValueError):
        pass
    return _clean_cache(filename)
