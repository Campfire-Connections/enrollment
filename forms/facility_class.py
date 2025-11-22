# enrollment/forms/facility.py

from core.forms.base import BaseForm
from course.models.facility_class import FacilityClass

from ..models.facility_class import FacilityClassEnrollment

class FacilityClassEnrollmentForm(BaseForm):
    """
    Form for managing FacilityClassEnrollment instances.
    """
    class Meta:
        model = FacilityClassEnrollment
        fields = ['facility_class', 'period', 'department', 'organization_enrollment']

    def __init__(self, *args, **kwargs):
        facility = kwargs.pop("facility", None)
        super().__init__(*args, **kwargs)

        qs = FacilityClass.objects.all()
        if facility:
            qs = qs.filter(facility_enrollment__facility=facility)
        self.fields["facility_class"].queryset = qs

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
