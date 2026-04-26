# enrollment/forms/faction.py
from django import forms
from django.db.models import F, Q
from django.utils.timezone import now

from facility.models.quarters import Quarters

from ..models.faction import FactionEnrollment
from ..models.facility import FacilityEnrollment
from ..models.temporal import Week


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
        fields = ["facility_enrollment", "week", "quarters"]

    def __init__(self, *args, **kwargs):
        self.faction = kwargs.pop("faction", None)
        super().__init__(*args, **kwargs)
        facility_enrollment = self._selected_facility_enrollment()
        week = self._selected_week()

        if facility_enrollment:
            self.fields["week"].queryset = Week.objects.filter(
                facility_enrollment=facility_enrollment
            )

        if week:
            quarters_qs = Quarters.objects.filter(
                facility=week.facility_enrollment.facility,
                capacity__gt=0,
            )
            quarters_qs = quarters_qs.exclude(
                week_availability__week=week,
                week_availability__reserved__gte=F("week_availability__capacity"),
            )
            if self.instance.pk and self.instance.quarters_id:
                quarters_qs = Quarters.objects.filter(
                    Q(pk=self.instance.quarters_id) | Q(pk__in=quarters_qs)
                )
            self.fields["quarters"].queryset = quarters_qs.distinct()

        if "facility_enrollment" in self.data:
            try:
                facility_enrollment_id = int(self.data.get("facility_enrollment"))
                self.fields["week"].queryset = Week.objects.filter(
                    facility_enrollment_id=facility_enrollment_id
                )
            except (ValueError, TypeError):
                self.fields["week"].queryset = Week.objects.none()

        if "week" in self.data:
            try:
                week_id = int(self.data.get("week"))
                week = Week.objects.select_related("facility_enrollment__facility").get(
                    pk=week_id
                )
                quarters_qs = Quarters.objects.filter(
                    facility=week.facility_enrollment.facility,
                    capacity__gt=0,
                ).exclude(
                    week_availability__week=week,
                    week_availability__reserved__gte=F("week_availability__capacity"),
                )
                if self.instance.pk and self.instance.quarters_id:
                    quarters_qs = Quarters.objects.filter(
                        Q(pk=self.instance.quarters_id) | Q(pk__in=quarters_qs)
                    )
                self.fields["quarters"].queryset = quarters_qs.distinct()
            except (ValueError, TypeError, Week.DoesNotExist):
                self.fields["quarters"].queryset = Quarters.objects.none()

    def _selected_facility_enrollment(self):
        if self.instance.pk:
            return self.instance.facility_enrollment
        value = self.initial.get("facility_enrollment")
        if isinstance(value, FacilityEnrollment):
            return value
        if value:
            try:
                return FacilityEnrollment.objects.get(pk=value)
            except (FacilityEnrollment.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _selected_week(self):
        if self.instance.pk:
            return self.instance.week
        value = self.initial.get("week")
        if isinstance(value, Week):
            return value
        if value:
            try:
                return Week.objects.select_related("facility_enrollment").get(pk=value)
            except (Week.DoesNotExist, ValueError, TypeError):
                return None
        return None
