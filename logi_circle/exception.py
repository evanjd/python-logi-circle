__all__ = [
    'UnexpectedContentType', 'BadSession', 'NoSession', 'BadCache'
]


class UnexpectedContentType(Exception):
    """When the wrong content type is received for a request"""


class BadSession(Exception):
    """Request made on a session that's no longer valid"""


class NoSession(Exception):
    """No session active"""


class BadCache(Exception):
    """Cached credentials incomplete, corrupt or do not apply to current user"""


class BadLogin(Exception):
    """Username or password rejected"""
