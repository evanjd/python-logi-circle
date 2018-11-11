"""Custom exceptions"""


class AuthorizationFailed(Exception):
    """When authorization fails for any reason."""


class NotAuthorized(Exception):
    """When supplied client ID has not been authorized."""
