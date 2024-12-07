# enrollment/forms/faculty.py

from core.forms.base import BaseForm
from facility.models.facility import Facility
from user.models import User

from ..models.faculty import FacultyEnrollment


class FacultyEnrollmentForm(BaseForm):
    class Meta:
        model = FacultyEnrollment
        fields = ["faculty", "facility_enrollment", "quarters", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of faculty and facilities
        self.fields["faculty"].queryset = User.objects.filter(user_type="FACULTY")
        self.fields["facility"].queryset = (
            Facility.objects.filter(organization=self.user.get_profile().organization)
            if self.user
            else Facility.objects.none()
        )

        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and end and start > end:
            self.add_error("end", "End date must be after the start date.")

        return cleaned_data
