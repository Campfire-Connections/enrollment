from django.core.exceptions import ValidationError
from django.db import transaction

from enrollment.models.availability import (
    FacilityClassAvailability,
    QuartersWeekAvailability,
)
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
