from django.core.exceptions import ValidationError
from django.db import transaction

from enrollment.models.availability import (
    FacilityClassAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.faculty import FacultyEnrollment
from enrollment.models.faculty_class import FacultyClassEnrollment as FacultyClassAssignment
from enrollment.models.leader import LeaderEnrollment


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
        attendee_class_enrollment=None,
    ):
        self._ensure_class_capacity(
            facility_class_enrollment, exclude=attendee_class_enrollment
        )
        enrollment = attendee_class_enrollment or AttendeeClassEnrollment()
        enrollment.attendee = attendee
        enrollment.attendee_enrollment = attendee_enrollment
        enrollment.facility_class_enrollment = facility_class_enrollment
        return self._persist(enrollment)

    def assign_faculty_to_class(
        self,
        *,
        faculty,
        facility_class_enrollment,
        faculty_enrollment=None,
        assignment=None,
    ):
        enrollment = assignment or FacultyClassAssignment()
        enrollment.faculty = faculty
        enrollment.facility_class_enrollment = facility_class_enrollment
        enrollment.faculty_enrollment = faculty_enrollment
        return self._persist(enrollment)

    def schedule_attendee_enrollment(
        self,
        *,
        attendee,
        faction_enrollment,
        quarters=None,
        attendee_enrollment=None,
        role=None,
    ):
        quarters = quarters or getattr(faction_enrollment, "quarters", None)
        if not quarters:
            raise ValidationError("Quarters are required for attendee enrollment.")
        self._ensure_attendee_capacity(
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
        return self._persist(enrollment)

    def schedule_faculty_enrollment(
        self,
        *,
        faculty,
        facility_enrollment,
        quarters,
        role=None,
        instance=None,
    ):
        self._ensure_faculty_quarters_capacity(
            facility_enrollment, quarters, exclude=instance
        )
        enrollment = instance or FacultyEnrollment()
        enrollment.faculty = faculty
        enrollment.facility_enrollment = facility_enrollment
        enrollment.quarters = quarters
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
        return self._persist(enrollment)

    def schedule_leader_enrollment(
        self,
        *,
        leader,
        faction_enrollment,
        quarters=None,
        leader_enrollment=None,
        role=None,
    ):
        quarters = quarters or getattr(faction_enrollment, "quarters", None)
        if not quarters:
            raise ValidationError("Quarters are required for leader enrollment.")
        self._ensure_leader_capacity(
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

    def _ensure_class_capacity(self, facility_class_enrollment, exclude=None):
        availability = FacilityClassAvailability.for_enrollment(
            facility_class_enrollment
        )
        remaining = availability.remaining
        if (
            exclude
            and getattr(exclude, "facility_class_enrollment_id", None)
            == facility_class_enrollment.id
        ):
            remaining += 1
        if remaining <= 0:
            raise ValidationError("This class is already at capacity.")

    def _ensure_attendee_capacity(
        self, faction_enrollment, quarters, exclude_attendee=None
    ):
        self._ensure_faction_quarters_capacity(
            faction_enrollment,
            quarters,
            exclude_attendee=exclude_attendee,
        )

    def _ensure_leader_capacity(
        self, faction_enrollment, quarters, exclude_leader=None
    ):
        self._ensure_faction_quarters_capacity(
            faction_enrollment,
            quarters,
            exclude_leader=exclude_leader,
        )

    def _ensure_faculty_quarters_capacity(
        self, facility_enrollment, quarters, exclude=None
    ):
        capacity = quarters.capacity or 1
        qs = FacultyEnrollment.objects.filter(
            facility_enrollment=facility_enrollment, quarters=quarters
        )
        if exclude is not None and getattr(exclude, "pk", None):
            qs = qs.exclude(pk=exclude.pk)
        if qs.count() >= capacity:
            raise ValidationError("Faculty quarters are already full.")

    def _ensure_faction_quarters_capacity(
        self,
        faction_enrollment,
        quarters,
        exclude_attendee=None,
        exclude_leader=None,
    ):
        capacity = quarters.capacity or 0
        if capacity <= 0:
            return
        occupied = self._calculate_quarters_usage(
            faction_enrollment,
            quarters,
            exclude_attendee=exclude_attendee,
            exclude_leader=exclude_leader,
        )
        if occupied >= capacity:
            raise ValidationError("Selected quarters are already full.")

    def _calculate_quarters_usage(
        self,
        faction_enrollment,
        quarters,
        exclude_attendee=None,
        exclude_leader=None,
    ):
        attendee_qs = AttendeeEnrollment.objects.filter(
            faction_enrollment=faction_enrollment, quarters=quarters
        )
        if exclude_attendee is not None and getattr(exclude_attendee, "pk", None):
            attendee_qs = attendee_qs.exclude(pk=exclude_attendee.pk)
        leader_qs = LeaderEnrollment.objects.filter(
            faction_enrollment=faction_enrollment, quarters=quarters
        )
        if exclude_leader is not None and getattr(exclude_leader, "pk", None):
            leader_qs = leader_qs.exclude(pk=exclude_leader.pk)
        return attendee_qs.count() + leader_qs.count()
