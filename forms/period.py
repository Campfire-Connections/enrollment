# enrollment/forms/period.py

from django import forms

from core.forms.base import BaseForm

from ..models.temporal import Period


class PeriodForm(BaseForm):
    start = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Start Time",
        required=True,
    )
    end = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="End Time",
        required=True,
    )

    class Meta:
        model = Period
        fields = ["name", "week", "start", "end"]

    def __init__(self, *args, facility=None, facility_enrollment=None, week=None, **kwargs):
        super().__init__(*args, **kwargs)

        if week:
            self.fields["week"].widget = forms.HiddenInput()
            self.fields["week"].initial = week.pk

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if not isinstance(start, str):
            raise forms.ValidationError("Invalid start time format.")

        if not isinstance(end, str):
            raise forms.ValidationError("Invalid end time format.")

        if start and end and start > end:
            self.add_error("end", "End time must be after the start time.")
        return cleaned_data
