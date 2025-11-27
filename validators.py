"""
Validation helpers for enrollment flows to keep business rules centralized.
"""

from typing import Optional
from django.core.exceptions import ValidationError

from enrollment.models.availability import (
    FacilityClassAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.faculty import FacultyEnrollment
from core.cache import cached
from enrollment.cache_keys import (
    quarters_usage_cache_key,
    invalidate_quarters_usage_cache,
)


def ensure_quarters_available(facility_enrollment, week, quarters) -> None:
    """
    Ensure quarters are free for a given week and facility enrollment.
    """
    availability, _ = QuartersWeekAvailability.objects.get_or_create(
        facility_enrollment=facility_enrollment,
        week=week,
        quarters=quarters,
        defaults={"capacity": quarters.capacity},
    )
    if availability.is_reserved:
        raise ValidationError("Selected quarters are already reserved for this week.")


def ensure_class_capacity(facility_class_enrollment, exclude=None) -> None:
    """
    Ensure class availability respects capacity, allowing an excluded enrollment.
    """
    availability = FacilityClassAvailability.for_enrollment(facility_class_enrollment)
    remaining = cached(
        availability.cache_key(),
        ttl=60,
        producer=lambda: availability.remaining,
    )
    if (
        exclude
        and getattr(exclude, "facility_class_enrollment_id", None)
        == facility_class_enrollment.id
    ):
        remaining += 1
    if remaining <= 0:
        raise ValidationError("This class is already at capacity.")


def ensure_faction_quarters_capacity(
    faction_enrollment,
    quarters,
    exclude_attendee: Optional[AttendeeEnrollment] = None,
    exclude_leader: Optional[LeaderEnrollment] = None,
) -> None:
    """
    Ensure faction quarters have capacity after accounting for exclusions.
    """
    capacity = quarters.capacity or 0
    if capacity <= 0:
        return
    occupied = _calculate_quarters_usage(
        faction_enrollment,
        quarters,
        exclude_attendee=exclude_attendee,
        exclude_leader=exclude_leader,
    )
    if occupied >= capacity:
        raise ValidationError("Selected quarters are already full.")


def ensure_attendee_capacity(
    faction_enrollment, quarters, exclude_attendee: Optional[AttendeeEnrollment] = None
) -> None:
    """
    Ensure attendee capacity in faction quarters.
    """
    ensure_faction_quarters_capacity(
        faction_enrollment, quarters, exclude_attendee=exclude_attendee
    )


def ensure_leader_capacity(
    faction_enrollment, quarters, exclude_leader: Optional[LeaderEnrollment] = None
) -> None:
    """
    Ensure leader capacity in faction quarters.
    """
    ensure_faction_quarters_capacity(
        faction_enrollment, quarters, exclude_leader=exclude_leader
    )


def ensure_faculty_quarters_capacity(
    facility_enrollment, quarters, exclude=None
) -> None:
    """
    Ensure faculty quarters have space, honoring an optional exclusion.
    """
    capacity = quarters.capacity or 1
    qs = FacultyEnrollment.objects.filter(
        facility_enrollment=facility_enrollment, quarters=quarters
    )
    if exclude is not None and getattr(exclude, "pk", None):
        qs = qs.exclude(pk=exclude.pk)
    if qs.count() >= capacity:
        raise ValidationError("Faculty quarters are already full.")


def _calculate_quarters_usage(
    faction_enrollment,
    quarters,
    exclude_attendee: Optional[AttendeeEnrollment] = None,
    exclude_leader: Optional[LeaderEnrollment] = None,
) -> int:
    """
    Compute occupied quarters count with optional exclusions.
    """
    key = quarters_usage_cache_key(
        getattr(faction_enrollment, "id", None), getattr(quarters, "id", None)
    )
    base_count = cached(
        key,
        ttl=60,
        producer=lambda: _raw_quarters_usage(faction_enrollment, quarters),
    )

    # Adjust for exclusions without blowing cache.
    if exclude_attendee is not None and getattr(exclude_attendee, "pk", None):
        base_count -= 1
    if exclude_leader is not None and getattr(exclude_leader, "pk", None):
        base_count -= 1
    return max(base_count, 0)


def _raw_quarters_usage(faction_enrollment, quarters) -> int:
    attendee_qs = AttendeeEnrollment.objects.filter(
        faction_enrollment=faction_enrollment, quarters=quarters
    ).count()
    leader_qs = LeaderEnrollment.objects.filter(
        faction_enrollment=faction_enrollment, quarters=quarters
    ).count()
    return attendee_qs + leader_qs
