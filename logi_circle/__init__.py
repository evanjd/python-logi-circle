"""Logi API"""
# coding: utf-8
# vim:sw=4:ts=4:et:
import sys
import logging
import json
import aiohttp


from .utils import _get_session_cookie, _handle_response, _exists_cache, _save_cache, _read_cache, _clean_cache
from .const import (
    API_URI, AUTH_ENDPOINT, CACHE_ATTRS, CACHE_FILE, CAMERAS_ENDPOINT, COOKIE_NAME, VALIDATE_ENDPOINT, HEADERS)
from .camera import Camera
from .exception import BadSession, NoSession, BadCache, BadLogin

_LOGGER = logging.getLogger(__name__)


class Logi():
    """A Python abstraction object to Logi Circle cameras."""

    def __init__(self, username, password, reuse_session=True, cache_file=CACHE_FILE):
        self.is_connected = False
        self.params = None
        self.username = username
        self.password = password

        self._session = None
        self._cache = CACHE_ATTRS
        self._cache_file = cache_file
        self._reuse_session = reuse_session

    async def login(self):
        """Create a session with the Logi Circle API"""
        # Close current session before creating a new one
        if isinstance(self._session, aiohttp.ClientSession):
            await self._session.close()

        if self._reuse_session:
            try:
                # Restore cached cookie and validate.
                await self._restore_cached_session()
            except BadCache:
                # Fall back to authentication if restoring the cached session fails.
                await self._authenticate()
        else:
            await self._authenticate()

    async def logout(self):
        """Close the session with the Logi Circle API"""
        _LOGGER.debug('Closing session for %s.', self.username)
        if isinstance(self._session, aiohttp.ClientSession):
            await self._session.close()
            self._session = None
            self.is_connected = False
        else:
            raise NoSession()

    async def _authenticate(self):
        """Authenticate user with the Logi Circle API."""
        url = API_URI + AUTH_ENDPOINT
        login_payload = {'email': self.username, 'password': self.password}

        _LOGGER.debug("POSTing login payload to %s", url)

        session = aiohttp.ClientSession()
        async with session.post(url, json=login_payload, headers=HEADERS) as req:
            # Handle failed authentication due to incorrect user/pass
            if req.status == 401:
                raise BadLogin(
                    'Username or password provided is incorrect. Could not authenticate.')

            # Throw error if authentication failed for any reason (connection issues, outage, etc)
            req.raise_for_status()

            self._session = session
            self.is_connected = True
            _LOGGER.info("Logged in as %s.", self.username)

            # Cache account and cookie for later use if reuse_session is true
            if self._reuse_session:
                try:
                    cookie = _get_session_cookie(session.cookie_jar)
                    _LOGGER.debug("Persisting session cookie %s", cookie)
                    self._cache['account'] = self.username
                    self._cache['cookie'] = cookie.value
                    _save_cache(self._cache, self._cache_file)
                except BadSession:
                    _LOGGER.error(
                        "Logi API authenticated successfully, but the session cookie wasn't returned.")
                    raise

    async def _restore_cached_session(self):
        """Retrieved cached cookie and validate session."""
        if _exists_cache(self._cache_file):
            _LOGGER.debug("Restoring cookie from cache.")

            self._cache = _read_cache(self._cache_file)

            if (self._cache['account'] is None) or (self._cache['cookie'] is None):
                # Cache is missing one or required values.
                _LOGGER.debug('Cache appears corrupt. Re-authenticating.')
                raise BadCache()
            elif self._cache['account'] != self.username:
                # Cache does not apply to this user.
                _LOGGER.debug(
                    'Cached credentials are for a different user. Re-authenticating.')
                raise BadCache()
            else:
                cookies = {COOKIE_NAME: self._cache['cookie']}

                session = aiohttp.ClientSession(cookies=cookies)
                async with session.get(API_URI + VALIDATE_ENDPOINT, headers=HEADERS) as req:
                    if req.status >= 300:
                        # Cookie has probably expired, reauthenticate.
                        raise BadCache()
                    else:
                        _LOGGER.info(
                            "Restored cached session for %s.", self.username)
                        self._session = session
                        self.is_connected = True

        else:
            raise BadCache()

    async def _fetch(self,
                     url,
                     method='GET',
                     params=None,
                     request_body=None,
                     relative_to_api_root=True,
                     raw=False,
                     _reattempt=False):
        """Query data from the Logi Circle API."""

        if self._session is None:
            await self.login()

        resolved_url = (API_URI + url if relative_to_api_root else url)
        _LOGGER.debug("Fetching %s (%s)", resolved_url, method)

        req = None

        # Perform request
        if method == 'GET':
            req = await self._session.get(resolved_url, headers=HEADERS, params=params)
        elif method == 'POST':
            req = await self._session.post(resolved_url, headers=HEADERS, params=params, json=request_body)
        elif method == 'PUT':
            req = await self._session.put(resolved_url, headers=HEADERS, params=params, json=request_body)
        else:
            raise ValueError('Method %s not supported.' % (method))

        _LOGGER.debug('Request %s (%s) returned %s',
                      resolved_url, method, req.status)

        # Handle response
        try:
            return await _handle_response(request=req, raw=raw)
        except BadSession:
            if _reattempt:
                # Welp, session still bad even after reauthenticating.
                _LOGGER.error(
                    'Session expired and a new session could not be established.')
                raise
            else:
                # Assume session expiry. Re-authenticate and try again.
                _LOGGER.debug(
                    'Session appears to have expired. Re-authenticating.')
                await self.login()
                return await self._fetch(url=url,
                                         method=method,
                                         params=params,
                                         request_body=request_body,
                                         relative_to_api_root=relative_to_api_root,
                                         raw=raw,
                                         _reattempt=True)

    @property
    def cookie(self):
        """Returns a cookie string that can be used for requests external to this library"""
        if self._session is None:
            return False
        return '%s=%s' % (COOKIE_NAME, _get_session_cookie(self._session.cookie_jar).value)

    @property
    async def cameras(self):
        """ Return all cameras. """
        cameras = []
        raw_cameras = await self._fetch(CAMERAS_ENDPOINT)

        for camera in raw_cameras:
            cameras.append(Camera(self, camera))

        return cameras
