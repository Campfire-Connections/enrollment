# enrollment/forms/facility.py

from core.forms.base import BaseForm
from course.models.facility_class import FacilityClass
from user.models import User

from ..models.facility import FacultyClassEnrollment

class FacultyClassEnrollmentForm(BaseForm):
    class Meta:
        model = FacultyClassEnrollment
        fields = ['faculty', 'facility_class', 'role', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of faculty and facility classes
        self.fields['faculty'].queryset = User.objects.filter(user_type="FACULTY")
        self.fields['facility_class'].queryset = FacilityClass.objects.filter(
            facility_enrollment__facility=self.user.facultyprofile.facility
        ) if self.user else FacilityClass.objects.none()

        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end and start > end:
            self.add_error('end', 'End date must be after the start date.')

        return cleaned_data
