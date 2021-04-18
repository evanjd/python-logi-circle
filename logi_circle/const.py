# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants"""
import os

# Requests and cached session properties
HEADERS = {
    'User-Agent': 'iOSClient/3.4.5.31',
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
UPDATE_REQUEST_THROTTLE = 5  # seconds

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
MODEL_GEN_1_NAME = '1st generation'
MODEL_GEN_2_NAME = '2nd generation'
MODEL_GEN_UNKNOWN_NAME = 'Unknown'
MODEL_GEN_1_MOUNT = 'Charging ring'
MODEL_GEN_2_MOUNT_WIRED = 'Wired'
MODEL_GEN_2_MOUNT_WIRELESS = 'Wireless'

# Feature mapping
FEATURES = {
    MODEL_GEN_1_MOUNT: ['is_charging', 'battery_level', 'last_activity_time', 'privacy_mode',
                        'signal_strength_percentage', 'signal_strength_category', 'speaker_volume', 'streaming_mode'],
    MODEL_GEN_2_MOUNT_WIRED: ['last_activity_time', 'privacy_mode', 'signal_strength_percentage',
                              'signal_strength_category', 'speaker_volume', 'streaming_mode'],
    MODEL_GEN_2_MOUNT_WIRELESS: ['is_charging', 'battery_level', 'last_activity_time', 'privacy_mode',
                                 'signal_strength_percentage', 'signal_strength_category', 'speaker_volume', 'streaming_mode'],
    MODEL_GEN_UNKNOWN_NAME: ['last_activity_time']
}
