# enrollment/forms/faculty_class.py

from django import forms
from django.core.exceptions import ValidationError

from core.forms.base import BaseForm
from user.models import User
from course.models.facility_class import FacilityClass

from ..models.facility import FacultyClassEnrollment

class FacultyClassEnrollmentForm(BaseForm):

    class Meta:
        model = FacultyClassEnrollment
        fields = ['faculty', 'facility_class', 'role', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with dynamic querysets and user context.
        """
        super().__init__(*args, **kwargs)

        # Dynamically filter the faculty queryset based on the user's facility
        if self.user and hasattr(self.user, 'facultyprofile'):
            facility = self.user.facultyprofile.facility
            self.fields['faculty'].queryset = Faculty.objects.filter(
                facultyprofile__facility=facility
            )
        else:
            self.fields['faculty'].queryset = Faculty.objects.none()

        # Dynamically filter facility classes based on facility
        self.fields['facility_class'].queryset = FacilityClass.objects.filter(
            facility_enrollment__facility=self.user.facultyprofile.facility
        ) if self.user else FacilityClass.objects.none()

        # Add default attributes to the fields
        self.fields['faculty'].widget.attrs.update({'class': 'form-control'})
        self.fields['facility_class'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['start_date'].widget.attrs.update({'class': 'form-control', 'type': 'date'})
        self.fields['end_date'].widget.attrs.update({'class': 'form-control', 'type': 'date'})

    def clean(self):
        """
        Add custom validation logic.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("The start date cannot be later than the end date.")

        return cleaned_data
