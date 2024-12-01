# enrollment/forms/facility.py

from django import forms

from core.forms.base import BaseForm
from facility.models import Facility

from ..models.organization import OrganizationEnrollment
from ..models.facility import FacilityEnrollment

class FacilityEnrollmentForm(BaseForm):
    class Meta:
        model = FacilityEnrollment
        fields = ['name', 'facility', 'organization_enrollment', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of facilities and organization enrollments
        self.fields['facility'].queryset = Facility.objects.filter(
            organization=self.user.get_profile().organization
        ) if self.user else Facility.objects.none()

        self.fields['organization_enrollment'].queryset = OrganizationEnrollment.objects.filter(
            organization=self.user.get_profile().organization
        ) if self.user else OrganizationEnrollment.objects.none()

        # Add classes to fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
