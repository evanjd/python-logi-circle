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
AUTH_ENDPOINT = "https://accounts.logi.com/identity/oauth2/authorize"
TOKEN_ENDPOINT = "https://accounts.logi.com/identity/oauth2/token"
DEFAULT_SCOPES = ("circle:activities_basic circle:activities circle:accessories circle:accessories_ro "
                  "circle:live_image circle:live circle:notifications circle:summaries")
AUTH_HEADER_KEY = "X-API-Key"

# API endpoints
API_BASE = "https://api.circle.logi.com/"