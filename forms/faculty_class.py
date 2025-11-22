# enrollment/forms/faculty_class.py

from django import forms

from core.forms.base import BaseForm
from facility.models.faculty import FacultyProfile
from enrollment.models.facility_class import (
    FacilityClassEnrollment as FacilityClassSchedule,
)
from enrollment.models.faculty import FacultyEnrollment as FacultyAssignment

from ..models.faculty_class import FacultyClassEnrollment

class FacultyClassEnrollmentForm(BaseForm):

    class Meta:
        model = FacultyClassEnrollment
        fields = ['faculty', 'facility_class_enrollment', 'faculty_enrollment']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with dynamic querysets and user context.
        """
        facility_override = kwargs.pop("facility", None)
        super().__init__(*args, **kwargs)

        user_profile = (
            getattr(self.user, "facultyprofile_profile", None) if self.user else None
        )
        facility = facility_override or getattr(user_profile, "facility", None)

        if facility:
            self.fields["faculty"].queryset = FacultyProfile.objects.filter(
                facility=facility
            ).select_related("user")
            self.fields["facility_class_enrollment"].queryset = (
                FacilityClassSchedule.objects.filter(
                    facility_class__facility_enrollment__facility=facility
                )
            )
        else:
            self.fields["faculty"].queryset = FacultyProfile.objects.none()
            self.fields["facility_class_enrollment"].queryset = (
                FacilityClassSchedule.objects.none()
            )

        if user_profile and not facility_override:
            enrollments_qs = user_profile.faculty_enrollments.all()
        elif facility:
            enrollments_qs = FacultyAssignment.objects.filter(
                facility_enrollment__facility=facility
            )
        else:
            enrollments_qs = FacultyAssignment.objects.none()

        self.fields["faculty_enrollment"].queryset = enrollments_qs

        # Add default attributes to the fields
        for name in self.fields:
            self.fields[name].widget.attrs.setdefault("class", "form-control")
