"""Subscription class"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import json
import aiohttp
from .const import MOTION_ACTIVITY_EVENTS
from .utils import _get_camera_from_id

_LOGGER = logging.getLogger(__name__)


class Subscription():
    """Generic implementation for a Logi Circle event subscription."""

    def __init__(self, wss_url, cameras):
        """Initialize Subscription object"""
        self.wss_url = wss_url
        self._cameras = cameras
        self._ws = None
        self._session = None

    async def open(self):
        """Establish a new WebSockets connection"""
        self._session = aiohttp.ClientSession()
        self._ws = await self._session.ws_connect(
            self.wss_url)
        _LOGGER.debug("Opened WS connection to url %s", self.wss_url)

    async def close(self):
        """Close WebSockets connection"""
        if isinstance(self._ws, aiohttp.ClientWebSocketResponse):
            await self._ws.close()
            self._ws = None

        if isinstance(self._session, aiohttp.ClientSession):
            await self._session.close()
            self._session = None

    async def get_next_event(self):
        """Wait for next WS frame"""
        _LOGGER.debug("WS: Waiting for next frame")
        msg = await self._ws.receive()

        if msg.data:
            self._handle_event(msg.data)

    def _handle_event(self, data):
        """Perform action with event"""
        event = json.loads(data)
        event_type = event['eventType']
        camera = _get_camera_from_id(event['eventData']['accessoryId'], self._cameras)

        _LOGGER.debug('WS: Got event %s for %s', event_type, camera.name)

        if event_type == "accessory_settings_changed":
            # Update camera props with changes
            camera._set_attributes(event['eventData'])
        elif event_type in MOTION_ACTIVITY_EVENTS:
            # Append event to camera's events list
            camera.events.append(event['eventData'])
        else:
            _LOGGER.warning('WS: Event type %s was unhandled', event_type)
