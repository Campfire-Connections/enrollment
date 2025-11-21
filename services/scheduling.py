from django.core.exceptions import ValidationError
from django.db import transaction

from enrollment.models.availability import (
    FacilityClassAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.faction import FactionEnrollment


class SchedulingService:
    """
    Centralized operations for faction and attendee scheduling so availability
    checks and error handling stay consistent across forms, APIs, and views.
    """

    def __init__(self, user=None):
        self.user = user

    def schedule_faction_enrollment(
        self,
        *,
        faction,
        facility_enrollment,
        week,
        quarters,
        start,
        end,
        **extra_fields,
    ):
        data = {
            "faction": faction,
            "facility_enrollment": facility_enrollment,
            "week": week,
            "quarters": quarters,
            "start": start,
            "end": end,
        }
        data.update(extra_fields)
        self._ensure_quarters_available(facility_enrollment, week, quarters)
        enrollment = FactionEnrollment(**data)
        return self._persist(enrollment)

    def assign_attendee_to_class(
        self,
        *,
        attendee,
        facility_class_enrollment,
        attendee_enrollment=None,
    ):
        self._ensure_class_capacity(facility_class_enrollment)
        enrollment = AttendeeClassEnrollment(
            attendee=attendee,
            attendee_enrollment=attendee_enrollment,
            facility_class_enrollment=facility_class_enrollment,
        )
        return self._persist(enrollment)

    def schedule_attendee_enrollment(
        self,
        *,
        attendee,
        faction_enrollment,
        quarters=None,
        attendee_enrollment=None,
        role=None,
        start=None,
        end=None,
    ):
        quarters = quarters or getattr(faction_enrollment, "quarters", None)
        if not quarters:
            raise ValidationError("Quarters are required for attendee enrollment.")
        self._ensure_attendee_capacity(
            faction_enrollment, quarters, exclude=attendee_enrollment
        )
        enrollment = attendee_enrollment or AttendeeEnrollment()
        enrollment.attendee = attendee
        enrollment.faction_enrollment = faction_enrollment
        enrollment.quarters = quarters
        if role is not None:
            enrollment.role = role
        enrollment.start = start or faction_enrollment.start
        enrollment.end = end or faction_enrollment.end
        if not enrollment.name:
            attendee_name = getattr(attendee, "user", None)
            attendee_name = (
                attendee_name.get_full_name().strip()
                if attendee_name
                else str(attendee)
            )
            week_label = getattr(faction_enrollment.week, "name", "")
            enrollment.name = (
                f"{attendee_name} ({week_label})" if week_label else attendee_name
            )
        return self._persist(enrollment)

    @transaction.atomic
    def _persist(self, enrollment):
        enrollment.full_clean()
        enrollment.save()
        return enrollment

    def _ensure_quarters_available(self, facility_enrollment, week, quarters):
        availability, _ = QuartersWeekAvailability.objects.get_or_create(
            facility_enrollment=facility_enrollment,
            week=week,
            quarters=quarters,
            defaults={"capacity": quarters.capacity},
        )
        if availability.is_reserved:
            raise ValidationError(
                "Selected quarters are already reserved for this week."
            )

    def _ensure_class_capacity(self, facility_class_enrollment):
        availability = FacilityClassAvailability.for_enrollment(
            facility_class_enrollment
        )
        if availability.remaining <= 0:
            raise ValidationError("This class is already at capacity.")

    def _ensure_attendee_capacity(
        self, faction_enrollment, quarters, exclude=None
    ):
        capacity = quarters.capacity or 0
        if capacity <= 0:
            return
        qs = AttendeeEnrollment.objects.filter(
            faction_enrollment=faction_enrollment, quarters=quarters
        )
        if exclude is not None and getattr(exclude, "pk", None):
            qs = qs.exclude(pk=exclude.pk)
        if qs.count() >= capacity:
            raise ValidationError("Selected quarters are already full.")
