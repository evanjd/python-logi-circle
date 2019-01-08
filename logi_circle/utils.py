"""Utilities library shared by the Logi, Camera and Activity classes."""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import slugify

_LOGGER = logging.getLogger(__name__)


def _write_to_file(data, filename, open_mode='wb'):  # pragma: no cover
    """Write binary object directly to file."""
    with open(filename, open_mode) as file_handle:
        file_handle.write(data)


async def _stream_to_file(stream, filename, open_mode='wb'):
    """Stream aiohttp response to file."""
    with open(filename, open_mode) as file_handle:
        while True:
            chunk = await stream.read(1024)
            if not chunk:
                break
            file_handle.write(chunk)


def _get_ids_for_cameras(cameras):
    """Get list of camera IDs from cameras"""
    return list(map(lambda camera: camera.id, cameras))


def _get_camera_from_id(camera_id, cameras):
    """Get Camera object from ID"""
    camera = list(filter(lambda cam: camera_id == cam.id, cameras))
    if camera:
        return camera[0]
    raise ValueError("No camera found with ID %s" % (camera_id))


def _slugify_string(text):
    """Slugify a given text."""
    return slugify.slugify(text, separator='_')
