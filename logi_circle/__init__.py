# coding: utf-8
# vim:sw=4:ts=4:et:
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import sys
import logging
import json
import requests
import aiohttp


from logi_circle.utils import _get_session_cookie, _exists_cache, _save_cache, _read_cache

from logi_circle.const import (
    API_URI, AUTH_ENDPOINT, CACHE_ATTRS, CACHE_FILE, CAMERAS_ENDPOINT, COOKIE_NAME, VALIDATE_ENDPOINT, HEADERS)

from logi_circle.camera import Camera

_LOGGER = logging.getLogger(__name__)


class Logi(object):
    """A Python abstraction object to Logi Circle cameras."""

    def __init__(self, username, password, reuse_session=True, cache_file=CACHE_FILE):
        self.is_connected = None
        self.params = None
        self.username = username
        self.password = password

        self._session = None
        self._cache = CACHE_ATTRS
        self._cache_file = cache_file
        self._reuse_session = reuse_session

    async def login(self):
        """Create a session with the Logi Circle API"""
        if self._reuse_session:
            try:
                await self._restore_cached_session()
            except AssertionError:
                # Fall back to authentication if restoring the cached session fails.
                await self._authenticate()
        else:
            await self._authenticate()

    async def logout(self):
        """Close the session with the Logi Circle API"""
        if isinstance(self._session, aiohttp.ClientSession):
            await self._session.close()
            self._session = None
        else:
            raise AssertionError('No session active.')

    async def _authenticate(self):
        """Authenticate user with the Logi Circle API."""
        url = API_URI + AUTH_ENDPOINT
        login_payload = {'email': self.username, 'password': self.password}

        _LOGGER.debug("POSTing login payload to %s", url)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=login_payload) as req:
                # Handle failed authentication due to incorrect user/pass
                if req.status == 401:
                    raise ValueError(
                        'Username or password provided is incorrect. Could not authenticate.')

                # Throw error if authentication failed for any reason (connection issues, outage, etc)
                req.raise_for_status()

                self._session = session
                self.is_connected = True
                _LOGGER.info("Logged in as %s.", self.username)

                # Cache account and cookie for later use if reuse_session is true
                if self._reuse_session:
                    cookie = _get_session_cookie(session.cookie_jar)
                    _LOGGER.debug("Persisting session cookie %s", cookie)
                    self._cache['account'] = self.username
                    self._cache['cookie'] = cookie.value
                    _save_cache(self._cache, self._cache_file)

    async def _restore_cached_session(self):
        """Retrieved cached cookie and validate session."""
        if _exists_cache(self._cache_file):
            _LOGGER.debug("Restoring cookie from cache.")

            self._cache = _read_cache(self._cache_file)

            if (self._cache['account'] is None) or (self._cache['cookie'] is None):
                # Cache is missing one or required values.
                _LOGGER.warn('Cache appears corrupt. Re-authenticating.')
                raise AssertionError('Cache incomplete.')
            elif (self._cache['account'] != self.username):
                # Cache does not apply to this user.
                _LOGGER.debug(
                    'Cached credentials are for a different user. Re-authenticating.')
                raise AssertionError('Cache does not apply to %s.')
            else:
                cookies = {COOKIE_NAME: self._cache['cookie']}

                async with aiohttp.ClientSession(cookies=cookies) as session:
                    async with session.get(API_URI + VALIDATE_ENDPOINT) as req:
                        if req.status >= 300:
                            # Cookie has probably expired, reauthenticate.
                            session.close()
                            raise AssertionError(
                                'Could not authenticate with cached cookie, likely gone stale.')
                        else:
                            _LOGGER.info(
                                "Restored cached session for %s.", self.username)
                            self._session = session

        else:
            raise AssertionError('Cache not found.')

    def _validate_session(self):
        """Perform a throwaway request to validate the session is still active, and attempt reauthentication if the session has in fact expired."""
        url = API_URI + VALIDATE_ENDPOINT

        req = self._session.get((url))
        if req.status_code != 200:
            # Cookie has expired, reauthenticate.
            _LOGGER.debug("Cookie has expired, re-authenticating.")
            self._authenticate()

        if self.is_connected is None:
            _LOGGER.info('Logged in with cached cookie.')
            self.is_connected = True

    def query(self,
              url,
              method='GET',
              params='',
              request_body=None,
              relative_to_api_root=True,
              raw=False,
              stream=False,
              headers=HEADERS,
              _reattempt=False):
        """Query data from the Logi Circle API."""
        resolved_url = (API_URI + url if relative_to_api_root else url)
        _LOGGER.debug("Querying %s", resolved_url)

        try:
            if method == 'GET':
                req = self._session.get(
                    (resolved_url), stream=stream, headers=headers, params=urlencode(params))
            elif method == 'PUT':
                req = self._session.put(
                    (resolved_url), stream=stream, headers=headers, params=urlencode(params), json=request_body)
            elif method == 'POST':
                req = self._session.post(
                    (resolved_url), stream=stream, headers=headers, params=urlencode(params), json=request_body)

            _LOGGER.debug("%s returned %s", resolved_url, req.status_code)

        except requests.exceptions.RequestException as err_msg:
            _LOGGER.error("Error: %s", err_msg)
            raise

        if req.status_code == 401:
            if _reattempt:
                # Should never happen, but want to guard against an infinite loop just in case.
                _LOGGER.error(
                    'Request to %s is returning 401 even after successfully reauthenticating.', resolved_url)
                req.raise_for_status()

            self.is_connected = False
            return self.query(url=url, method=method, params=params, request_body=request_body, relative_to_api_root=relative_to_api_root, raw=raw, stream=stream, headers=headers, _reattempt=True)

        if raw:
            return req
        return req.json()

    @property
    def cameras(self):
        """ Return all cameras. """
        cameras = []
        raw_cameras = self.query(CAMERAS_ENDPOINT)

        for camera in raw_cameras:
            cameras.append(Camera(self, camera))

        return cameras
