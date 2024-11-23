# enrollment/forms/period.py

from django import forms
from ..models.temporal import Period, Week

class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['name', 'description', 'week', 'start', 'end']

    def __init__(self, *args, **kwargs):
        week = kwargs.pop('week', None)  # Accept the 'week' from view kwargs
        super().__init__(*args, **kwargs)

        # Pre-fill the week dropdown if provided
        if week:
            self.fields['week'].queryset = Week.objects.filter(pk=week.pk)
            self.fields['week'].initial = week.pk
            self.fields['week'].widget.attrs['readonly'] = True
            self.fields['week'].widget = forms.HiddenInput()
        else:
            self.fields['week'].queryset = Week.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        # Ensure start is before end
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start and end and start >= end:
            raise forms.ValidationError("Start time must be before end time.")
        
        return cleaned_data
