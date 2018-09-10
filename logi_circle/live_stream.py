"""Live Stream class"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import asyncio
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from .const import (PROTOCOL, ACCESSORIES_ENDPOINT,
                    LIVESTREAM_ENDPOINT, LIVESTREAM_XMLNS)
from .utils import _stream_to_file, _write_to_file

_LOGGER = logging.getLogger(__name__)


class LiveStream():
    """Logi Circle DASH client."""

    def __init__(self, camera, logi):
        """Initialize LiveStream object."""
        self._camera = camera
        self._logi = logi
        self._initialisation_file = None
        self._index = None
        self._initialised = False
        self._mpd_data = {}
        self._next_segment_time = None
        self._last_filename = None

    def _get_mpd_url(self):
        """Returns the URL for the MPD file"""
        return '%s://%s/api%s/%s%s' % (PROTOCOL, self._camera.node_id,
                                       ACCESSORIES_ENDPOINT, self._camera.id, LIVESTREAM_ENDPOINT)

    async def _get_init_mp4(self, base_url, header_url):
        """Downloads the initialisation file and returns a bytes object"""
        url = '%s%s' % (base_url, header_url)

        header = await self._logi._fetch(
            url=url, relative_to_api_root=False, raw=True)

        header_data = await header.read()
        header.close()
        return header_data

    async def _get_mpd(self):
        """Gets the MPD XML and extracts the data required to download segments"""

        # Force an update to get the latest node ID
        await self._camera.update(force=True)

        # Get MPD XML and save to raw_xml var
        url = self._get_mpd_url()

        xml_req = await self._logi._fetch(
            url=url, relative_to_api_root=False, raw=True)
        raw_xml = await xml_req.read()
        xml_req.close()

        # Extract data from MPD XML
        xml = ET.fromstring(raw_xml)
        stream_config = {}
        stream_config['base_url'] = xml.find(
            './{%s}BaseURL' % (LIVESTREAM_XMLNS)).text
        stream_config['header_url'] = xml.find('.//{%s}SegmentTemplate' %
                                               (LIVESTREAM_XMLNS)).get('initialization')
        stream_config['stream_filename_template'] = xml.find(
            './/{%s}SegmentTemplate' % (LIVESTREAM_XMLNS)).get('media')
        stream_config['start_index'] = int(xml.find('.//{%s}SegmentTemplate' %
                                                    (LIVESTREAM_XMLNS)).get('startNumber'))
        stream_config['segment_length'] = int(xml.find('.//{%s}SegmentTemplate' %
                                                       (LIVESTREAM_XMLNS)).get('duration'))
        return stream_config

    def _build_mp4(self, segment_file):
        """Concatenates the initialisation data and segment file to return a playable MP4"""

        return self._initialisation_file + segment_file

    def _set_next_segment_time(self):
        """Sets the time that the next segment should be ready to download"""
        duration = self._mpd_data['segment_length']
        self._next_segment_time = datetime.now() + timedelta(milliseconds=duration)

    def _get_time_before_next_segment(self):
        """Time before the next segment is available, in seconds"""
        delay = self._next_segment_time - datetime.now()
        delay_in_seconds = delay.total_seconds()
        return 0 if delay_in_seconds < 0 else delay_in_seconds

    def _get_segment_url(self):
        """Builds the URL to get the next video segment"""
        base_url = self._mpd_data['base_url']
        stream_filename_template = self._mpd_data['stream_filename_template']

        file_name = stream_filename_template.replace(
            '$Number$', str(self._index))
        return '%s%s' % (base_url, file_name)

    async def get_segment(self, filename=None, append=True):
        """Returns the current segment video from the live stream"""
        # Initialise if required
        if self._initialised is False:
            await self._initialise()

        # Get current wait time and set timer for next download
        wait_time = self._get_time_before_next_segment()
        self._set_next_segment_time()

        _LOGGER.debug(
            'Sleeping for %s seconds before grabbing next live stream segment.', wait_time)
        # And sleep, if needed.
        if wait_time > 0:
            await asyncio.sleep(wait_time)

        # Get segment data
        url = self._get_segment_url()
        segment = await self._logi._fetch(
            url=url, relative_to_api_root=False, raw=True)

        # Increment segment counter
        self._index += 1

        if filename:
            if filename == self._last_filename and append:
                # Append to existing file
                _LOGGER.debug(
                    'Appending video segment to %s', filename)
                await _stream_to_file(stream=segment.content, filename=filename, open_mode='ab')
                segment.close()
            else:
                # Write init header and segment (init a new file)
                _LOGGER.debug(
                    'Writing init header and segment to file %s', filename)
                _write_to_file(self._initialisation_file, filename)
                await _stream_to_file(stream=segment.content, filename=filename, open_mode='ab')
                segment.close()
            self._last_filename = filename
        else:
            # Return binary object
            content = await segment.read()
            segment.close()
            return self._build_mp4(content)

    async def _initialise(self):
        """Sets up the live stream so that it's ready to output video data"""

        # Get stream config and cache header
        self._mpd_data = await self._get_mpd()
        self._initialisation_file = await self._get_init_mp4(self._mpd_data['base_url'], self._mpd_data['header_url'])
        self._index = self._mpd_data['start_index']
        self._initialised = True

        # Delay stream until one segment is ready
        self._set_next_segment_time()
