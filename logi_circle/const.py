# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants"""
import os

# Requests and cached session properties
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Origin': 'https://circle.logi.com',
    'Accept': '*/*',
    'Referer': 'https://circle.logi.com/',
    'Pragma': 'no-cache'
}
CACHE_ATTRS = {'cookie': None, 'account': None}
try:
    CACHE_FILE = os.path.join(os.getenv("HOME"), '.logi_circle-session.cache')
except (AttributeError, TypeError):
    CACHE_FILE = os.path.join('.', '.logi_circle-session.cache')
COOKIE_NAME = 'prod_session'

# Date formats
# Yes, we're hard-coding the timezone. "%z" is a py37 only feature,
# and we know the Logi API always returns dates in UTC.
ISO8601_FORMAT_MASK = '%Y-%m-%dT%H:%M:%SZ'

# API endpoints
PROTOCOL = 'https'
API_HOST = 'video.logi.com'
API_URI = '%s://%s/api' % (PROTOCOL, API_HOST)
AUTH_ENDPOINT = '/accounts/authorization'
CAMERAS_ENDPOINT = '/accessories'
IMAGES_ENDPOINT = '/image'
LIVESTREAM_ENDPOINT = '/mpd'
ACTIVITIES_ENDPOINT = '/activities'
ACCESSORIES_ENDPOINT = '/accessories'
VALIDATE_ENDPOINT = '/accounts/self'

# Misc
JPEG_CONTENT_TYPE = 'image/jpeg'
VIDEO_CONTENT_TYPE = 'application/octet-stream'
LIVESTREAM_XMLNS = 'urn:mpeg:dash:schema:mpd:2011'

# Model to product mapping
MODEL_GEN_1 = 'A1533'
MODEL_GEN_2 = 'V-R0008'
MODEL_TYPE_GEN_1 = '1st gen'
MODEL_TYPE_GEN_2_WIRED = '2nd gen - wired'
MODEL_TYPE_GEN_2_WIRELESS = '2nd gen - wireless'
MODEL_TYPE_UNKNOWN = 'Unknown'

# Feature mapping
FEATURES = {
    MODEL_TYPE_GEN_1: ['is_charging', 'battery_level', 'last_activity_time', 'privacy_mode',
                       'signal_strength_percentage', 'signal_strength_category'],
    MODEL_TYPE_GEN_2_WIRED: ['last_activity_time', 'privacy_mode', 'signal_strength_percentage', 'signal_strength_category'],
    MODEL_TYPE_GEN_2_WIRELESS: ['is_charging', 'battery_level', 'last_activity_time', 'privacy_mode',
                                'signal_strength_percentage', 'signal_strength_category'],
    MODEL_TYPE_UNKNOWN: ['last_activity_time']
}
