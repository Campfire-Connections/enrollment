from typing import Optional

from django.db import transaction
from django.core.exceptions import ValidationError

from enrollment.models.enrollment import ActiveEnrollment
from core.logging import log_event


class ActiveEnrollmentService:
    """
    Centralized operations around a user's active enrollment to keep
    uniqueness and cleanup consistent across views/forms/handlers.
    """

    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def set_active(
        self,
        *,
        attendee_enrollment: Optional[ActiveEnrollment.attendee_enrollment.field.related_model] = None,
        leader_enrollment: Optional[ActiveEnrollment.leader_enrollment.field.related_model] = None,
        faction_enrollment: Optional[ActiveEnrollment.faction_enrollment.field.related_model] = None,
        faculty_enrollment: Optional[ActiveEnrollment.faculty_enrollment.field.related_model] = None,
        facility_enrollment: Optional[ActiveEnrollment.facility_enrollment.field.related_model] = None,
    ) -> ActiveEnrollment:
        enrollments = [
            attendee_enrollment,
            leader_enrollment,
            faction_enrollment,
            faculty_enrollment,
            facility_enrollment,
        ]
        if sum(bool(enrollment) for enrollment in enrollments) != 1:
            raise ValidationError(
                "Exactly one active enrollment type must be provided."
            )

        # Clear any existing records for this user to enforce one active slot.
        ActiveEnrollment.objects.filter(user=self.user).delete()

        active_enrollment = ActiveEnrollment.objects.create(
            user=self.user,
            attendee_enrollment=attendee_enrollment,
            leader_enrollment=leader_enrollment,
            faction_enrollment=faction_enrollment,
            faculty_enrollment=faculty_enrollment,
            facility_enrollment=facility_enrollment,
        )
        log_event(
            "active_enrollment.set",
            actor_id=getattr(self.user, "id", None),
            extra={
                "attendee_enrollment_id": getattr(attendee_enrollment, "id", None),
                "leader_enrollment_id": getattr(leader_enrollment, "id", None),
                "faction_enrollment_id": getattr(faction_enrollment, "id", None),
                "faculty_enrollment_id": getattr(faculty_enrollment, "id", None),
                "facility_enrollment_id": getattr(facility_enrollment, "id", None),
            },
        )
        return active_enrollment
