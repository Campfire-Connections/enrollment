# enrollment/forms/faculty.py

from core.forms.base import BaseForm
from facility.models.faculty import FacultyProfile

from ..models.faculty import FacultyEnrollment


class FacultyEnrollmentForm(BaseForm):
    class Meta:
        model = FacultyEnrollment
        fields = ["faculty", "facility_enrollment", "quarters", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of faculty and facilities
        self.fields["faculty"].queryset = FacultyProfile.objects.select_related("user")

        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
