# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants"""
import os

# Requests and cached session properties
HEADERS = {
    'content-type': 'application/json; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://circle.logi.com',
    'Accept': '*/*',
    'Referer': 'https://circle.logi.com/',
    'Host': 'video.logi.com',
    'Pragma': 'no-cache'
}
CACHE_ATTRS = {'cookie': None, 'account': None}
try:
    CACHE_FILE = os.path.join(os.getenv("HOME"), '.logi_circle-session.cache')
except (AttributeError, TypeError):
    CACHE_FILE = os.path.join('.', '.logi_circle-session.cache')
COOKIE_NAME = 'prod_session'

# Date formats
ISO8601_FORMAT_MASK = '%Y-%m-%dT%H:%M:%S%z'

# API endpoints
PROTOCOL = 'https'
API_URI = '%s://video.logi.com/api' % (PROTOCOL)
AUTH_ENDPOINT = '/accounts/authorization'
CAMERAS_ENDPOINT = '/accessories'
IMAGES_ENDPOINT = '/image'
ACTIVITIES_ENDPOINT = '/activities'
ACCESSORIES_ENDPOINT = '/accessories'
VALIDATE_ENDPOINT = '/accounts/self'

# Misc
JPEG_MIME_TYPE = 'image/jpeg'
