# enrollment/forms/faculty_class.py

from django import forms
from django.core.exceptions import ValidationError

from core.forms.base import BaseForm
from user.models import User
from course.models.facility_class import FacilityClass

from ..models.faculty_class import FacultyClassEnrollment

class FacultyClassEnrollmentForm(BaseForm):

    class Meta:
        model = FacultyClassEnrollment
        fields = ['faculty', 'facility_class_enrollment', 'faculty_enrollment']

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
        self.fields['facility_class_enrollment'].widget.attrs.update({'class': 'form-control'})
        self.fields['faculty_enrollment'].widget.attrs.update({'class': 'form-control'})
        
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
