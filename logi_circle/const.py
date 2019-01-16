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
# Relative to API root
NOTIFICATIONS_ENDPOINT = "/api/accounts/self/notifications"
ACCOUNT_ENDPOINT = "/api/accounts/self"
ACCESSORIES_ENDPOINT = "/api/accessories"
ACTIVITIES_ENDPOINT = "/activities"
# Relative to camera root
CONFIG_ENDPOINT = "/config"
LIVE_IMAGE_ENDPOINT = "/live/image"
LIVE_RTSP_ENDPOINT = "/live/rtsp"
# Relative to activity root
ACTIVITY_IMAGE_ENDPOINT = "/image"
ACTIVITY_MP4_ENDPOINT = "/mp4"
ACTIVITY_DASH_ENDPOINT = "/mpd"
ACTIVITY_HLS_ENDPOINT = "/hls/activity.m3u8"

# Headers
ACCEPT_IMAGE_HEADER = {"Accept": "image/jpeg"}
ACCEPT_VIDEO_HEADER = {"Accept": "video/mp4"}

# Misc
DEFAULT_IMAGE_QUALITY = 75
DEFAULT_IMAGE_REFRESH = False
DEFAULT_FFMPEG_BIN = "ffmpeg"
ISO8601_FORMAT_MASK = '%Y-%m-%dT%H:%M:%SZ'
ACTIVITY_API_LIMIT = 100
GEN_1_MODEL = "A1533"
GEN_2_MODEL = "V-R0008"
GEN_1_MOUNT = "Charging Ring"
GEN_2_MOUNT_WIRE = "Wired"
GEN_2_MOUNT_WIREFREE = "Wire-free"  # Battery powered
MOUNT_UNKNOWN = "Unknown"
ACTIVITY_EVENTS = ["activity_created",
                   "activity_updated",
                   "activity_finished"]

# Prop to API mapping
PROP_MAP = {
    "id": {"key": "accessoryId", "required": True},
    "name": {"key": "name", "required": True, "settable": True},
    "mac_address": {"key": "mac", "required": True},
    "connected": {"key": "isConnected", "default_value": False},
    "model": {"key": "modelNumber"},
    "streaming": {"key": "streamingEnabled", "config": True, "default_value": False, "settable": True},
    "charging": {"key": "batteryCharging", "config": True},
    "battery_saving": {"key": "saveBattery", "config": True},
    "timezone": {"key": "timeZone", "config": True, "default_value": "UTC", "settable": True},
    "battery_level": {"key": "batteryLevel", "config": True, "default_value": -1},
    "signal_strength_percentage": {"key": "wifiSignalStrength", "config": True},
    "firmware": {"key": "firmwareVersion", "config": True},
    "microphone": {"key": "microphoneOn", "config": True, "default_value": False},
    "microphone_gain": {"key": "microphoneGain", "config": True},
    "pir_wake_up": {"key": "pirWakeUp", "config": True, "default_value": False},
    "speaker": {"key": "speakerOn", "config": True, "default_value": False},
    "speaker_volume": {"key": "speakerVolume", "config": True},
    "led": {"key":  "ledEnabled", "config": True, "default_value": False},
    "recording_disabled": {"key": "privacyMode", "config": True, "default_value": False, "settable": True}
}

# Feature mapping
FEATURES_MAP = {
    GEN_1_MOUNT: ["activity",
                  "charging",
                  "battery_level",
                  "last_activity_time",
                  "recording",
                  "signal_strength_percentage",
                  "signal_strength_category",
                  "speaker_volume",
                  "streaming"],
    GEN_2_MOUNT_WIRE: ["activity",
                       "last_activity_time",
                       "recording",
                       "signal_strength_percentage",
                       "signal_strength_category",
                       "speaker_volume",
                       "streaming"],
    GEN_2_MOUNT_WIREFREE: ["activity",
                           "charging",
                           "battery_level",
                           "last_activity_time",
                           "recording",
                           "signal_strength_percentage",
                           "signal_strength_category",
                           "speaker_volume",
                           "streaming"],
    MOUNT_UNKNOWN: ["last_activity_time"]
}
