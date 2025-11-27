import logging
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.faculty import FacultyEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty_class import FacultyClassEnrollment as FacultyClassAssignment
from enrollment.models.leader import LeaderEnrollment
from enrollment.validators import (
    ensure_attendee_capacity,
    ensure_class_capacity,
    ensure_faculty_quarters_capacity,
    ensure_faction_quarters_capacity,
    ensure_leader_capacity,
    ensure_quarters_available,
)
from core.logging import log_event

logger = logging.getLogger(__name__)


class SchedulingService:
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
        **extra_fields,
    ) -> FactionEnrollment:
        data = {
            "faction": faction,
            "facility_enrollment": facility_enrollment,
            "week": week,
            "quarters": quarters,
            "start": start,
            "end": end,
        }
        data.update(extra_fields)
        ensure_quarters_available(facility_enrollment, week, quarters)
        enrollment = FactionEnrollment(**data)
        enrollment = self._persist(enrollment)
        self._log(
            "faction.schedule",
            faction_id=getattr(faction, "id", None),
            facility_enrollment_id=getattr(facility_enrollment, "id", None),
            week_id=getattr(week, "id", None),
        )
        return enrollment

    def assign_attendee_to_class(
        self,
        *,
        attendee,
        facility_class_enrollment: FacilityClassEnrollment,
        attendee_enrollment=None,
        attendee_class_enrollment: Optional[AttendeeClassEnrollment] = None,
    ) -> AttendeeClassEnrollment:
        ensure_class_capacity(
            facility_class_enrollment, exclude=attendee_class_enrollment
        )
        enrollment = attendee_class_enrollment or AttendeeClassEnrollment()
        enrollment.attendee = attendee
        enrollment.attendee_enrollment = attendee_enrollment
        enrollment.facility_class_enrollment = facility_class_enrollment
        enrollment = self._persist(enrollment)
        self._log(
            "attendee.assign_class",
            attendee_id=getattr(attendee, "id", None),
            facility_class_enrollment_id=getattr(facility_class_enrollment, "id", None),
        )
        return enrollment

    def drop_attendee_from_class(
        self, *, attendee_class_enrollment: AttendeeClassEnrollment
    ) -> None:
        if not attendee_class_enrollment.pk:
            return
        enrollment_id = attendee_class_enrollment.pk
        attendee_class_enrollment.delete()
        self._log("attendee.drop_class", attendee_class_enrollment_id=enrollment_id)

    def drop_faculty_from_class(
        self, *, faculty_class_enrollment: FacultyClassAssignment
    ) -> None:
        if not faculty_class_enrollment.pk:
            return
        enrollment_id = faculty_class_enrollment.pk
        faculty_class_enrollment.delete()
        self._log("faculty.drop_class", faculty_class_enrollment_id=enrollment_id)

    def swap_attendee_class(
        self,
        *,
        attendee_class_enrollment: AttendeeClassEnrollment,
        new_facility_class_enrollment: FacilityClassEnrollment,
    ) -> AttendeeClassEnrollment:
        return self.assign_attendee_to_class(
            attendee=attendee_class_enrollment.attendee,
            facility_class_enrollment=new_facility_class_enrollment,
            attendee_enrollment=attendee_class_enrollment.attendee_enrollment,
            attendee_class_enrollment=attendee_class_enrollment,
        )

    def assign_faculty_to_class(
        self,
        *,
        faculty,
        facility_class_enrollment: FacilityClassEnrollment,
        faculty_enrollment=None,
        assignment=None,
    ) -> FacultyClassAssignment:
        enrollment = assignment or FacultyClassAssignment()
        enrollment.faculty = faculty
        enrollment.facility_class_enrollment = facility_class_enrollment
        enrollment.faculty_enrollment = faculty_enrollment
        enrollment = self._persist(enrollment)
        self._log(
            "faculty.assign_class",
            faculty_id=getattr(faculty, "id", None),
            facility_class_enrollment_id=getattr(facility_class_enrollment, "id", None),
        )
        return enrollment

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
        enrollment = self._persist(enrollment)
        self._log(
            "faculty.schedule",
            faculty_id=getattr(faculty, "id", None),
            facility_enrollment_id=getattr(facility_enrollment, "id", None),
        )
        return enrollment

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
        enrollment.save()
        return enrollment
