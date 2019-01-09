"""LiveStream class, representing a Logi Circle camera's live stream"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import subprocess
from .const import (ACCESSORIES_ENDPOINT,
                    LIVE_IMAGE_ENDPOINT,
                    LIVE_RTSP_ENDPOINT,
                    ACCEPT_IMAGE_HEADER,
                    DEFAULT_IMAGE_QUALITY,
                    DEFAULT_IMAGE_REFRESH)
from .utils import _stream_to_file

_LOGGER = logging.getLogger(__name__)


class LiveStream():
    """Generic implementation for Logi Circle live stream."""

    def __init__(self, logi, camera):
        """Initialise Logi Camera object."""
        self.logi = logi
        self.camera_id = camera.id

    def get_jpeg_url(self):
        """Get URL for camera JPEG snapshot"""
        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.camera_id, LIVE_IMAGE_ENDPOINT)
        return url

    async def download_jpeg(self,
                            quality=DEFAULT_IMAGE_QUALITY,
                            refresh=DEFAULT_IMAGE_REFRESH,
                            filename=None):
        """Download the most recent snapshot image for this camera"""

        url = self.get_jpeg_url()
        params = {'quality': quality, 'refresh': str(refresh).lower()}

        image = await self.logi._fetch(url=url, raw=True, headers=ACCEPT_IMAGE_HEADER, params=params)
        if filename:
            await _stream_to_file(image.content, filename)
            image.close()
            return True
        content = await image.read()
        image.close()
        return content

    async def get_rtsp_url(self):
        """Get RTSP stream URL."""
        # Request RTSP stream
        url = '%s/%s%s' % (ACCESSORIES_ENDPOINT, self.camera_id, LIVE_RTSP_ENDPOINT)
        stream_resp_payload = await self.logi._fetch(url=url)

        # Return time-limited RTSP URI
        rtsp_uri = stream_resp_payload["rtsp_uri"].replace('rtsp://', 'rtsps://')
        return rtsp_uri

    async def download_rtsp(self,
                            duration,  # in seconds
                            filename,
                            ffmpeg_bin=None):
        """Downloads the live stream into a specific file for a specific duration"""

        ffmpeg_bin = ffmpeg_bin or self.logi.ffmpeg_path

        # Bail now if ffmpeg is missing
        if ffmpeg_bin is None:
            raise RuntimeError(
                "This method requires ffmpeg to be installed and available from the current execution context.")

        rtsp_uri = await self.get_rtsp_url()
        subprocess.check_call(
            [ffmpeg_bin, "-i", rtsp_uri, "-t", str(duration),
             "-vcodec", "copy", "-acodec", "copy", filename],
            stderr=subprocess.DEVNULL
        )
