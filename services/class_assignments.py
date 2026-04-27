from typing import Optional

from django.db import transaction

from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty_class import FacultyClassEnrollment as FacultyClassAssignment
from enrollment.validators import ensure_class_capacity


class ClassAssignmentSchedulingMixin:
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
        previous_class_id = getattr(enrollment, "facility_class_enrollment_id", None)
        reservation_changed = previous_class_id != getattr(
            facility_class_enrollment, "id", None
        )
        enrollment.attendee = attendee
        enrollment.attendee_enrollment = attendee_enrollment
        enrollment.facility_class_enrollment = facility_class_enrollment
        with transaction.atomic():
            enrollment = self._persist(enrollment)
            if reservation_changed:
                self._reserve_attendee_class(enrollment)
                self._release_attendee_class_by_id(previous_class_id)
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
        class_id = getattr(
            attendee_class_enrollment, "facility_class_enrollment_id", None
        )
        with transaction.atomic():
            self._release_attendee_class_by_id(class_id)
            attendee_class_enrollment.delete()
        self._log("attendee.drop_class", attendee_class_enrollment_id=enrollment_id)

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
        with transaction.atomic():
            enrollment = self._persist(enrollment)
        self._log(
            "faculty.assign_class",
            faculty_id=getattr(faculty, "id", None),
            facility_class_enrollment_id=getattr(facility_class_enrollment, "id", None),
        )
        return enrollment

    def drop_faculty_from_class(
        self, *, faculty_class_enrollment: FacultyClassAssignment
    ) -> None:
        if not faculty_class_enrollment.pk:
            return
        enrollment_id = faculty_class_enrollment.pk
        with transaction.atomic():
            faculty_class_enrollment.delete()
        self._log("faculty.drop_class", faculty_class_enrollment_id=enrollment_id)
