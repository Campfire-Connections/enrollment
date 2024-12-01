from django import forms

from core.forms.base import BaseForm
from organization.models.organization import Organization
from course.models.organization_course import OrganizationCourse

from ..models.organization import OrganizationCourseEnrollment

class OrganizationCourseEnrollmentForm(BaseForm):
    class Meta:
        model = OrganizationCourseEnrollment
        fields = ['name', 'organization', 'organization_course', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of organizations and courses
        self.fields['organization'].queryset = Organization.objects.filter(
            id=self.user.get_profile().organization_id
        ) if self.user else Organization.objects.none()

        self.fields['organization_course'].queryset = OrganizationCourse.objects.filter(
            organization=self.user.get_profile().organization
        ) if self.user else OrganizationCourse.objects.none()

        # Add classes to fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
