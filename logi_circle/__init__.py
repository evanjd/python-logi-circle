# coding: utf-8
# vim:sw=4:ts=4:et:
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import sys
import logging
import requests
import json

from logi_circle.utils import _exists_cache, _save_cache, _read_cache

from logi_circle.const import (
    API_URI, AUTH_ENDPOINT, CACHE_ATTRS, CACHE_FILE, CAMERAS_ENDPOINT, COOKIE_NAME, VALIDATE_ENDPOINT, HEADERS)

from logi_circle.camera import Camera

_LOGGER = logging.getLogger(__name__)


class Logi(object):
    """A Python abstraction object to Logi Circle cameras."""

    def __init__(self, username, password, debug=True, reuse_session=True, cache_file=CACHE_FILE):
        self.is_connected = None
        self.params = None

        self.debug = debug
        self.username = username
        self.password = password
        self.session = requests.Session()

        if debug:
            _LOGGER.setLevel(logging.DEBUG)

        self.cache = CACHE_ATTRS
        self.cache_file = cache_file
        self._reuse_session = reuse_session

        if self._reuse_session:
            self._restore_cached_session()
        else:
            self._authenticate()

    def _authenticate(self):
        """Authenticate user with the Logi Circle API."""
        url = API_URI + AUTH_ENDPOINT
        login_payload = {'email': self.username, 'password': self.password}

        _LOGGER.debug("POSTing login payload to %s", url)

        sys.exit()

        try:
            req = self.session.post((url), json=login_payload)
            req.raise_for_status()

            self.is_connected = True
            _LOGGER.info("Logged in.")
            self.params = {
                'auth_cookie': req.cookies[COOKIE_NAME]}

            # Cache account and cookie for later use if reuse_session is true
            if self._reuse_session:
                cookie = req.cookies[COOKIE_NAME]
                _LOGGER.debug("Persisting session cookie %s", cookie)
                self.cache['account'] = self.username
                self.cache['cookie'] = cookie
                _save_cache(self.cache, self.cache_file)

        except requests.exceptions.RequestException as err_msg:
            _LOGGER.error("Error: %s", err_msg)
            raise

    def _restore_cached_session(self):
        """Retrieved cached cookie and validate session."""
        if _exists_cache(self.cache_file):
            _LOGGER.debug("Restoring cookie from cache.")

            self.cache = _read_cache(self.cache_file)

            if (self.cache['account'] is None) or (self.cache['cookie'] is None):
                # Cache is missing one or required values.
                _LOGGER.warn('Cache appears corrupt. Re-authenticating.')
                self._authenticate()
            else:
                # Add cookie to session
                self.session.cookies.set(COOKIE_NAME, self.cache['cookie'])
                self._validate_session()

        else:
            self._authenticate()

    def _validate_session(self):
        """Perform a throwaway request to validate the session is still active, and attempt reauthentication if the session has in fact expired."""
        url = API_URI + VALIDATE_ENDPOINT

        req = self.session.get((url))
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
              _reattempt=False):
        """Query data from the Logi Circle API."""
        resolved_url = (API_URI + url if relative_to_api_root else url)
        _LOGGER.debug("Querying %s", resolved_url)

        try:
            if method == 'GET':
                req = self.session.get(
                    (resolved_url), params=urlencode(params))
            elif method == 'PUT':
                req = self.session.put(
                    (resolved_url), params=urlencode(params), json=request_body)
            elif method == 'POST':
                req = self.session.post(
                    (resolved_url), params=urlencode(params), json=request_body)

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
            return self.query(resolved_url, method, params, request_body, relative_to_api_root, raw, True)

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
