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
        super().__init__(*args, **kwargs)

        # Optionally filter FacilityClass if there's context like facility
        if 'facility' in kwargs:
            self.fields['facility_class'].queryset = FacilityClass.objects.filter(
                facility=kwargs['facility']
            )
        else:
            self.fields['facility_class'].queryset = FacilityClass.objects.all()

        # Add common styling or attributes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        """
        Custom validation logic for start_date and end_date fields.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', "End date must be after the start date.")

        return cleaned_data
