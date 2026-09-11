from django.conf import settings

DEFAULTS = {
    "ENABLED": True,
    "SLOW_QUERY_MS": 100,
    "N_PLUS_ONE_THRESHOLD": 5,
}


def get(key):
    """Read a setting from settings.QUERYSCOPE, falling back to the default."""
    return {**DEFAULTS, **getattr(settings, "QUERYSCOPE", {})}[key]
