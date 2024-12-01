# enrollment/forms/week.py

from django import forms

from core.forms.base import BaseForm

from ..models.facility import FacilityEnrollment
from ..models.temporal import Week


class WeekForm(BaseForm):
    class Meta:
        model = Week
        fields = ["name", "facility_enrollment", "start", "end"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of facility enrollments
        self.fields["facility_enrollment"].queryset = (
            FacilityEnrollment.objects.filter(
                facility=self.user.facultyprofile.facility
            )
            if self.user
            else FacilityEnrollment.objects.none()
        )

        # Add classes to fields
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and end and start > end:
            self.add_error("end", "End date must be after the start date.")
        return cleaned_data
