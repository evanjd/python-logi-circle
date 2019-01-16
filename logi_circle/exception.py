"""Custom exceptions"""


class AuthorizationFailed(Exception):
    """When authorization fails for any reason."""


class NotAuthorized(Exception):
    """When supplied client ID has not been authorized."""


class SubscriptionClosed(Exception):
    """When requesting the next WebSockets frame on an already closed subscription."""
