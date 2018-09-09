"""Utilities library shared by the Logi, Camera and Activity classes."""
# coding: utf-8
# vim:sw=4:ts=4:et:
import os
import functools
import subprocess
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from logi_circle.const import (
    CACHE_ATTRS, COOKIE_NAME)
from .exception import BadSession

_LOGGER = logging.getLogger(__name__)


def _get_session_cookie(cookie_jar):
    """Iterates through the session's AbstractCookieJar and returns the cookie relevant to Logi API sessions."""
    for cookie in cookie_jar:
        if cookie.key == COOKIE_NAME:
            return cookie
    raise BadSession()


async def _handle_response(request, raw):
    """Generic response handler, intended to transparently handle session expiry."""
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
    """Stream aiohttp response to file."""
    with open(filename, open_mode) as file_handle:
        while True:
            chunk = await stream.read(1024)
            if not chunk:
                break
            file_handle.write(chunk)


def _write_to_file(data, filename, open_mode='wb'):
    """Write binary object directly to file."""
    with open(filename, open_mode) as file_handle:
        file_handle.write(data)


def _delete_quietly(filename):
    """Deletes a file which may or may not exist."""
    try:
        os.remove(filename)
    except OSError:
        pass


def _get_file_duration(file):
    """Get the duration in milliseconds of a video using ffprobe."""
    output = subprocess.check_output(
        ['ffprobe', '-i', file, '-show_entries',
         'format=duration', '-v', 'quiet', '-of', 'csv=p=0'],
        stderr=subprocess.STDOUT
    )
    return int(float(output) * 1000)


def _truncate_video(input_file, output_file, seconds):
    """Truncates a video based on the input duration"""
    subprocess.check_call(
        ['ffmpeg', '-y', '-i', input_file, '-t', str(seconds),
         '-f', 'mp4', '-c', 'copy', output_file],
        stderr=subprocess.DEVNULL
    )


def _get_first_frame_from_video(file):
    """Returns the first frame of a video as a bytes object using ffmpeg."""
    output = subprocess.check_output(
        ['ffmpeg', '-i', file, '-vf',
         'select=eq(n\\,0)', '-q:v', '3', '-f', 'singlejpeg', '-'],
        stderr=subprocess.DEVNULL
    )
    return output


def _ffmpeg_installed():
    """Returns a bool indicating whether ffmpeg is installed."""
    try:
        subprocess.check_call(["ffmpeg", "-version"],
                              stdout=subprocess.DEVNULL)
        return True
    except OSError:
        _LOGGER.warning(
            'ffmpeg is not installed! Not all API methods will function.')
        return False


_FFMPEG_INSTALLED = _ffmpeg_installed()


def requires_ffmpeg(func):
    """Decorator to guard against ffmpeg use if it's not installed."""
    @functools.wraps(func)
    def wrapped_decorator(*args, **kwargs):
        if not _FFMPEG_INSTALLED:
            raise RuntimeError(
                'This method requires ffmpeg to be installed and available from the current execution context.')
        else:
            return func(*args, **kwargs)
    return wrapped_decorator


def _write_to_file(data, filename):
    """Write bytes data to file."""
    with open(filename, 'wb') as file_handle:
        file_handle.write(data)


def _clean_cache(filename):
    """Remove filename if pickle version mismatch."""
    if os.path.isfile(filename):
        os.remove(filename)

    # Initialise cache since file was removed
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

            if data.keys() != CACHE_ATTRS.keys():
                raise EOFError
            return data

    except (EOFError, ValueError):
        pass
    return _clean_cache(filename)
