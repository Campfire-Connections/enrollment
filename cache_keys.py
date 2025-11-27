"""
Cache key utilities for enrollment-related aggregates.
"""

from django.core.cache import cache


def quarters_usage_cache_key(faction_enrollment_id, quarters_id) -> str:
    return f"quarters_usage:{faction_enrollment_id}:{quarters_id}"


def invalidate_quarters_usage_cache(faction_enrollment_id, quarters_id) -> None:
    cache.delete(quarters_usage_cache_key(faction_enrollment_id, quarters_id))
