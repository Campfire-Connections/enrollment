from django import forms
from django.utils.timezone import now

from ..models.leader import LeaderEnrollment
from ..models.faction import FactionEnrollment
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
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        faction_enrollments = FactionEnrollment.objects.with_related().filter(
            start__year__gte=now().year,
            start__year__lte=now().year + 1,
        )
        leader_profile = getattr(user, "leaderprofile_profile", None) if user else None
        if leader_profile and leader_profile.faction_id:
            faction_enrollments = faction_enrollments.filter(
                faction=leader_profile.faction
            )
        self.fields["faction_enrollment"].queryset = faction_enrollments

        faction_enrollment = self._selected_faction_enrollment()
        if faction_enrollment:
            self.fields["quarters"].queryset = Quarters.objects.filter(
                facility=faction_enrollment.facility_enrollment.facility,
                capacity__gt=0,
            )

        if leader_profile:
            self.fields["leader"].initial = leader_profile

    def clean(self):
        """
        Perform custom validation (if necessary) to ensure form logic integrity.
        """
        cleaned_data = super().clean()

        # Example: Check if the selected faction_enrollment and quarters are compatible.
        faction_enrollment = cleaned_data.get("faction_enrollment")
        quarters = cleaned_data.get("quarters")
        if faction_enrollment and quarters:
            facility = faction_enrollment.facility_enrollment.facility
            if facility != quarters.facility:
                self.add_error(
                    "quarters",
                    "Selected quarters do not match the facility enrollment.",
                )

        return cleaned_data

    def _selected_faction_enrollment(self):
        if self.instance.pk:
            return self.instance.faction_enrollment
        value = self.data.get("faction_enrollment") if self.data else None
        if value:
            try:
                return FactionEnrollment.objects.with_related().get(pk=value)
            except (FactionEnrollment.DoesNotExist, ValueError, TypeError):
                return None
        value = self.initial.get("faction_enrollment")
        if isinstance(value, FactionEnrollment):
            return value
        if value:
            try:
                return FactionEnrollment.objects.with_related().get(pk=value)
            except (FactionEnrollment.DoesNotExist, ValueError, TypeError):
                return None
        return None
