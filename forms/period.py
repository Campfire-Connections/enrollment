# enrollment/forms/period.py

from core.forms.base import BaseForm

from ..models.temporal import Week, Period

class PeriodForm(BaseForm):
    class Meta:
        model = Period
        fields = ['name', 'week', 'start', 'end']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamic filtering of weeks
        self.fields['week'].queryset = Week.objects.filter(
            facility_enrollment__facility=self.user.facultyprofile.facility
        ) if self.user else Week.objects.none()

        # Add classes to fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')

        if start and end and start > end:
            self.add_error('end', 'End date must be after the start date.')
        return cleaned_data
