# enrollment/forms/facility.py

from django import forms

from ..models.facility import FacilityClass

class FacilityClassForm(forms.ModelForm):
    class Meta:
        model = FacilityClass
        fields = ['name', 'description', 'organization_course', 'facility_enrollment']
