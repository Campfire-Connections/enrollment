import logging
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.availability import (
    FacilityClassAvailability,
    FacultyQuartersAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.faction import FactionEnrollment
from enrollment.models.faculty import FacultyEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.cache_keys import invalidate_quarters_usage_cache
from enrollment.services.class_assignments import ClassAssignmentSchedulingMixin
from enrollment.validators import (
    ensure_attendee_capacity,
    ensure_faculty_quarters_capacity,
    ensure_leader_capacity,
    ensure_quarters_available,
)
from core.logging import log_event

logger = logging.getLogger(__name__)


class SchedulingService(ClassAssignmentSchedulingMixin):
    """
    Centralized operations for faction and attendee scheduling so availability
    checks and error handling stay consistent across forms, APIs, and views.
    """

    def __init__(self, user=None):
        self.user = user

    def _log(self, action: str, **payload) -> None:
        actor_id = getattr(self.user, "id", None)
        log_event(f"scheduling.{action}", actor_id=actor_id, extra=payload)

    def schedule_faction_enrollment(
        self,
        *,
        faction,
        facility_enrollment,
        week,
        quarters,
        start,
        end,
        faction_enrollment: Optional[FactionEnrollment] = None,
        **extra_fields,
    ) -> FactionEnrollment:
        enrollment = faction_enrollment or FactionEnrollment()
        previous = self._faction_reservation_key(enrollment)
        next_key = self._reservation_key(facility_enrollment, week, quarters)
        reservation_changed = self._reservation_scope(previous) != next_key

        if reservation_changed:
            ensure_quarters_available(facility_enrollment, week, quarters)

        enrollment.faction = faction
        enrollment.facility_enrollment = facility_enrollment
        enrollment.week = week
        enrollment.quarters = quarters
        enrollment.start = start
        enrollment.end = end
        for field, value in extra_fields.items():
            setattr(enrollment, field, value)

        with transaction.atomic():
            enrollment = self._persist(enrollment)
            if reservation_changed:
                self._reserve_faction_quarters(enrollment)
                self._release_faction_quarters_by_key(previous)
            self._invalidate_faction_usage(enrollment.pk, enrollment.quarters_id)
            if previous:
                self._invalidate_faction_usage(previous[3], previous[2])
        self._log(
            "faction.schedule",
            faction_id=getattr(faction, "id", None),
            facility_enrollment_id=getattr(facility_enrollment, "id", None),
            week_id=getattr(week, "id", None),
        )
        return enrollment

    def drop_faction_enrollment(self, *, faction_enrollment: FactionEnrollment) -> None:
        if not faction_enrollment.pk:
            return
        enrollment_id = faction_enrollment.pk
        reservation = self._faction_reservation_key(faction_enrollment)
        with transaction.atomic():
            self._release_faction_quarters_by_key(reservation)
            faction_enrollment.delete()
            self._invalidate_faction_usage(
                enrollment_id, getattr(faction_enrollment, "quarters_id", None)
            )
        self._log("faction.drop", faction_enrollment_id=enrollment_id)

    def schedule_attendee_enrollment(
        self,
        *,
        attendee,
        faction_enrollment,
        quarters=None,
        attendee_enrollment: Optional[AttendeeEnrollment] = None,
        role=None,
    ) -> AttendeeEnrollment:
        quarters = quarters or getattr(faction_enrollment, "quarters", None)
        if not quarters:
            raise ValidationError("Quarters are required for attendee enrollment.")
        ensure_attendee_capacity(
            faction_enrollment, quarters, exclude_attendee=attendee_enrollment
        )
        enrollment = attendee_enrollment or AttendeeEnrollment()
        enrollment.attendee = attendee
        enrollment.faction_enrollment = faction_enrollment
        enrollment.quarters = quarters
        if role is not None:
            enrollment.role = role
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
        with transaction.atomic():
            enrollment = self._persist(enrollment)
        self._log(
            "attendee.schedule",
            attendee_id=getattr(attendee, "id", None),
            faction_enrollment_id=getattr(faction_enrollment, "id", None),
        )
        return enrollment

    def schedule_faculty_enrollment(
        self,
        *,
        faculty,
        facility_enrollment,
        quarters,
        role=None,
        instance=None,
    ) -> FacultyEnrollment:
        ensure_faculty_quarters_capacity(
            facility_enrollment, quarters, exclude=instance
        )
        enrollment = instance or FacultyEnrollment()
        previous = self._faculty_reservation_key(enrollment)
        next_key = self._reservation_key(facility_enrollment, None, quarters)
        reservation_changed = self._reservation_scope(previous) != next_key
        enrollment.faculty = faculty
        enrollment.facility_enrollment = facility_enrollment
        enrollment.quarters = quarters
        if facility_enrollment and not enrollment.start:
            enrollment.start = facility_enrollment.start
        if facility_enrollment and not enrollment.end:
            enrollment.end = facility_enrollment.end
        if role is not None:
            enrollment.role = role
        if not enrollment.name:
            faculty_name = getattr(faculty, "user", None)
            faculty_name = (
                faculty_name.get_full_name().strip()
                if faculty_name
                else str(faculty)
            )
            session_label = facility_enrollment.facility.name
            enrollment.name = f"{faculty_name} ({session_label})"
        with transaction.atomic():
            enrollment = self._persist(enrollment)
            if reservation_changed:
                self._reserve_faculty_quarters(enrollment)
                self._release_faculty_quarters_by_key(previous)
        self._log(
            "faculty.schedule",
            faculty_id=getattr(faculty, "id", None),
            facility_enrollment_id=getattr(facility_enrollment, "id", None),
        )
        return enrollment

    def drop_faculty_enrollment(self, *, faculty_enrollment: FacultyEnrollment) -> None:
        if not faculty_enrollment.pk:
            return
        enrollment_id = faculty_enrollment.pk
        reservation = self._faculty_reservation_key(faculty_enrollment)
        with transaction.atomic():
            self._release_faculty_quarters_by_key(reservation)
            faculty_enrollment.delete()
        self._log("faculty.drop", faculty_enrollment_id=enrollment_id)

    def schedule_leader_enrollment(
        self,
        *,
        leader,
        faction_enrollment,
        quarters=None,
        leader_enrollment=None,
        role=None,
    ) -> LeaderEnrollment:
        quarters = quarters or getattr(faction_enrollment, "quarters", None)
        if not quarters:
            raise ValidationError("Quarters are required for leader enrollment.")
        ensure_leader_capacity(
            faction_enrollment, quarters, exclude_leader=leader_enrollment
        )
        enrollment = leader_enrollment or LeaderEnrollment()
        enrollment.leader = leader
        enrollment.faction_enrollment = faction_enrollment
        enrollment.quarters = quarters
        if role is not None:
            enrollment.role = role
        if not enrollment.name:
            leader_name = getattr(leader, "user", None)
            leader_name = (
                leader_name.get_full_name().strip() if leader_name else str(leader)
            )
            week_label = getattr(faction_enrollment.week, "name", "")
            enrollment.name = (
                f"{leader_name} ({week_label})" if week_label else leader_name
            )
        with transaction.atomic():
            enrollment = self._persist(enrollment)
        self._log(
            "leader.schedule",
            leader_id=getattr(leader, "id", None),
            faction_enrollment_id=getattr(faction_enrollment, "id", None),
        )
        return enrollment

    @transaction.atomic
    def _persist(self, enrollment):
        enrollment.full_clean()
        try:
            enrollment.save()
        except IntegrityError as exc:
            raise ValidationError(
                "This enrollment conflicts with an existing assignment."
            ) from exc
        return enrollment

    def _reservation_key(self, facility_enrollment, week, quarters):
        facility_enrollment_id = getattr(facility_enrollment, "id", None)
        quarters_id = getattr(quarters, "id", None)
        if not facility_enrollment_id or not quarters_id:
            return None
        return (
            facility_enrollment_id,
            getattr(week, "id", None),
            quarters_id,
        )

    def _reservation_scope(self, key):
        if not key:
            return None
        return key[:3]

    def _faction_reservation_key(self, enrollment):
        if not getattr(enrollment, "pk", None):
            return None
        return (
            enrollment.facility_enrollment_id,
            enrollment.week_id,
            enrollment.quarters_id,
            enrollment.pk,
        )

    def _faculty_reservation_key(self, enrollment):
        if not getattr(enrollment, "pk", None):
            return None
        return (
            enrollment.facility_enrollment_id,
            None,
            enrollment.quarters_id,
            enrollment.pk,
        )

    def _reserve_faction_quarters(self, enrollment):
        availability, _ = QuartersWeekAvailability.objects.get_or_create(
            facility_enrollment=enrollment.facility_enrollment,
            week=enrollment.week,
            quarters=enrollment.quarters,
            defaults={"capacity": enrollment.quarters.capacity},
        )
        availability.reserve_full()

    def _release_faction_quarters_by_key(self, key):
        if not key:
            return
        facility_enrollment_id, week_id, quarters_id, _ = key
        try:
            availability = QuartersWeekAvailability.objects.get(
                facility_enrollment_id=facility_enrollment_id,
                week_id=week_id,
                quarters_id=quarters_id,
            )
        except QuartersWeekAvailability.DoesNotExist:
            return
        availability.release_full()

    def _reserve_faculty_quarters(self, enrollment):
        availability, _ = FacultyQuartersAvailability.objects.get_or_create(
            facility_enrollment=enrollment.facility_enrollment,
            quarters=enrollment.quarters,
            defaults={"capacity": enrollment.quarters.capacity or 1},
        )
        availability.reserve_slot()

    def _release_faculty_quarters_by_key(self, key):
        if not key:
            return
        facility_enrollment_id, _, quarters_id, _ = key
        try:
            availability = FacultyQuartersAvailability.objects.get(
                facility_enrollment_id=facility_enrollment_id,
                quarters_id=quarters_id,
            )
        except FacultyQuartersAvailability.DoesNotExist:
            return
        availability.release_slot()

    def _reserve_attendee_class(self, enrollment):
        if not enrollment.facility_class_enrollment_id:
            return
        availability = FacilityClassAvailability.for_enrollment(
            enrollment.facility_class_enrollment
        )
        availability.reserve()

    def _release_attendee_class_by_id(self, facility_class_enrollment_id):
        if not facility_class_enrollment_id:
            return
        try:
            availability = FacilityClassAvailability.objects.get(
                facility_class_enrollment_id=facility_class_enrollment_id
            )
        except FacilityClassAvailability.DoesNotExist:
            return
        availability.release()

    def _invalidate_faction_usage(self, faction_enrollment_id, quarters_id):
        invalidate_quarters_usage_cache(faction_enrollment_id, quarters_id)
