# enrollment/forms/facility.py

from core.forms.base import BaseForm

from ..models.facility import FacilityClassEnrollment

class FacilityClassEnrollmentForm(BaseForm):
    class Meta:
        model = FacilityClassEnrollment
        fields = ['name', 'description', 'organization_course', 'facility_enrollment']
