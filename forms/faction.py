# enrollment/forms/faction.py
from django import forms
from ..models.faction import FactionEnrollment
from ..models.facility import FacilityEnrollment
from ..models.temporal import Week
from facility.models.quarters import Quarters
from django.utils.timezone import now

class FactionEnrollmentForm(forms.ModelForm):
    facility_enrollment = forms.ModelChoiceField(
        queryset=FacilityEnrollment.objects.filter(
            start__year__gte=now().year, 
            start__year__lte=now().year + 1
        ),
        label="Facility Enrollment",
        empty_label="Select Facility",
    )
    week = forms.ModelChoiceField(
        queryset=Week.objects.none(),
        label="Week",
        required=True,
    )
    quarters = forms.ModelChoiceField(
        queryset=Quarters.objects.none(),
        label="Quarters (Faction)",
        required=True,
    )

    class Meta:
        model = FactionEnrollment
        fields = ['facility_enrollment', 'week', 'quarters'] #, 'start_date', 'end_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Init method to load dynamic form data
        if 'facility_enrollment' in self.data:
            try:
                facility_enrollment_id = int(self.data.get('facility_enrollment'))
                self.fields['week'].queryset = Week.objects.filter(
                    facility_enrollment_id=facility_enrollment_id
                )
            except (ValueError, TypeError):
                self.fields['week'].queryset = Week.objects.none()

        if 'week' in self.data:
            try:
                week_id = int(self.data.get('week'))
                self.fields['quarters'].queryset = Quarters.objects.filter(
                    availability__week_id=week_id,
                    availability__capacity__gt=0,
                ).distinct()
            except (ValueError, TypeError):
                self.fields['quarters'].queryset = Quarters.objects.none()
