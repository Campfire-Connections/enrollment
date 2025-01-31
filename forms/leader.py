from django import forms
from django.utils.timezone import now

from ..models.leader import LeaderEnrollment
from ..models.faction import FactionEnrollment
from ..models.temporal import Week
from facility.models.quarters import Quarters


class LeaderEnrollmentForm(forms.ModelForm):
    faction_enrollment = forms.ModelChoiceField(
        queryset=FactionEnrollment.objects.none(),
        label="Facility Enrollment",
        empty_label="Select Facility",
    )
    quarters = forms.ModelChoiceField(
        queryset=Quarters.objects.none(),
        label="Quarters (Leader)",
        required=False,
    )

    class Meta:
        model = LeaderEnrollment
        fields = ["leader", "faction_enrollment", "quarters", "role"]

    def __init__(self, *args, **kwargs):
        """
        Customize the form initialization to dynamically set querysets based on 
        additional context (e.g., user or other parameters).
        """
        # Retrieve the current user from kwargs (if provided).
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Dynamically filter faction_enrollment based on the current year.
        self.fields["faction_enrollment"].queryset = FactionEnrollment.objects.filter(
            start__year__gte=now().year,
            start__year__lte=now().year + 1,
        )

        # Dynamically filter quarters based on the user's faction (if available).
        if user and hasattr(user, "leaderprofile_profile"):
            faction = user.leaderprofile_profile.faction
            self.fields["quarters"].queryset = Quarters.objects.filter(faction=faction)

        # Optionally, set an initial value for leader if available.
        if user:
            self.fields["leader"].initial = user.leaderprofile_profile

    def clean(self):
        """
        Perform custom validation (if necessary) to ensure form logic integrity.
        """
        cleaned_data = super().clean()

        # Example: Check if the selected faction_enrollment and quarters are compatible.
        faction_enrollment = cleaned_data.get("faction_enrollment")
        quarters = cleaned_data.get("quarters")
        if faction_enrollment and quarters:
            if faction_enrollment.facility != quarters.facility:
                self.add_error("quarters", "Selected quarters do not match the facility enrollment.")

        return cleaned_data

    
