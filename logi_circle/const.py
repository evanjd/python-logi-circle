# coding: utf-8
# vim:sw=4:ts=4:et:
"""Constants"""
import os

try:
    DEFAULT_CACHE_FILE = os.path.join(
        os.getenv("HOME"), '.logi_circle-session.cache')
except (AttributeError, TypeError):
    DEFAULT_CACHE_FILE = os.path.join('.', '.logi_circle-session.cache')

# OAuth2 constants
AUTH_HOST = "accounts.logi.com"
AUTH_BASE = "https://%s" % (AUTH_HOST)
AUTH_ENDPOINT = "/identity/oauth2/authorize"
TOKEN_ENDPOINT = "/identity/oauth2/token"
DEFAULT_SCOPES = ("circle:activities_basic circle:activities circle:accessories circle:accessories_ro "
                  "circle:live_image circle:live circle:notifications circle:summaries")

# API endpoints
API_HOST = "api.circle.logi.com"
API_BASE = "https://%s" % (API_HOST)
ACCESSORIES_ENDPOINT = "/api/accessories"
LIVE_IMAGE_ENDPOINT = "/live/image"

# Headers
ACCEPT_IMAGE_HEADER = {'Accept': 'image/jpeg'}

# Misc
DEFAULT_IMAGE_QUALITY = 75
DEFAULT_IMAGE_REFRESH = False
