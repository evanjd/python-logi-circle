"""Utilities library shared by the Logi, Camera and Activity classes."""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging

_LOGGER = logging.getLogger(__name__)


def _write_to_file(data, filename, open_mode='wb'):
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
