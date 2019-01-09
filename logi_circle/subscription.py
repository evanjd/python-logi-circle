"""Subscription class"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import logging
import json
import aiohttp
from .const import ACTIVITY_EVENTS, ACCESSORIES_ENDPOINT, ACTIVITIES_ENDPOINT
from .utils import _get_camera_from_id
from .activity import Activity

_LOGGER = logging.getLogger(__name__)


class Subscription():
    """Generic implementation for a Logi Circle event subscription."""

    def __init__(self, wss_url, cameras, raw=False):
        """Initialize Subscription object"""
        self.wss_url = wss_url
        self._cameras = cameras
        self._ws = None
        self._session = None
        self._raw = raw

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
        if self._session is None:
            await self.open()

        _LOGGER.debug("WS: Waiting for next frame")
        msg = await self._ws.receive()

        if self._raw:
            return msg
        if msg.data:
            self._handle_event(msg.data)

        return msg

    @property
    def is_open(self):
        """Returns a bool indicating whether the subscription is active."""
        return bool(self._ws)

    @staticmethod
    def _handle_activity(event_type, event, camera):
        """Controls the camera's current_activity prop based on incoming activity events."""

        if event_type in ['activity_created', 'activity_updated']:
            # Set camera's current activity prop to this activity
            camera._current_activity = Activity(activity=event,
                                                url='%s/%s%s' % (ACCESSORIES_ENDPOINT, camera.id, ACTIVITIES_ENDPOINT),
                                                local_tz=camera._local_tz,
                                                logi=camera.logi)

        if event_type == 'activity_finished':
            # Clear current activity prop
            camera._current_activity = None

    def _handle_event(self, data):
        """Perform action with event"""
        event = json.loads(data)
        event_type = event['eventType']
        camera = _get_camera_from_id(event['eventData']['accessoryId'], self._cameras)

        _LOGGER.debug('WS: Got event %s for %s', event_type, camera.name)

        if event_type == "accessory_settings_changed":
            # Update camera props with changes
            camera._set_attributes(event['eventData'])
        elif event_type in ACTIVITY_EVENTS:
            # Append event to camera's events list
            Subscription._handle_activity(event_type, event['eventData'], camera)
        else:
            _LOGGER.warning('WS: Event type %s was unhandled', event_type)
