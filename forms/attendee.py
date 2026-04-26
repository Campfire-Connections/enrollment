from django import forms

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faction import FactionEnrollment
from facility.models.quarters import Quarters
from faction.models.attendee import AttendeeProfile


class AttendeeEnrollmentForm(forms.ModelForm):
    class Meta:
        model = AttendeeEnrollment
        fields = ["attendee", "faction_enrollment", "quarters", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        faction_enrollment = self._selected_faction_enrollment()
        self.fields["faction_enrollment"].queryset = FactionEnrollment.objects.with_related()
        self.fields["attendee"].queryset = AttendeeProfile.objects.select_related(
            "user", "faction"
        )
        if faction_enrollment:
            self.fields["attendee"].queryset = self.fields["attendee"].queryset.filter(
                faction=faction_enrollment.faction
            )
            self.fields["quarters"].queryset = Quarters.objects.filter(
                facility=faction_enrollment.facility_enrollment.facility,
                capacity__gt=0,
            )
        else:
            self.fields["quarters"].queryset = Quarters.objects.none()
        self._apply_form_control_class()

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

    def _apply_form_control_class(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class AttendeeClassEnrollmentForm(forms.ModelForm):
    class Meta:
        model = AttendeeClassEnrollment
        fields = ["attendee", "attendee_enrollment", "facility_class_enrollment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attendee_enrollment = self._selected_attendee_enrollment()
        self.fields["attendee"].queryset = AttendeeProfile.objects.select_related(
            "user", "faction"
        )
        self.fields["attendee_enrollment"].queryset = (
            AttendeeEnrollment.objects.select_related(
                "attendee__user", "faction_enrollment__facility_enrollment"
            )
        )
        if attendee_enrollment:
            self.fields["attendee"].queryset = self.fields["attendee"].queryset.filter(
                pk=attendee_enrollment.attendee_id
            )
            self.fields["facility_class_enrollment"].queryset = (
                FacilityClassEnrollment.objects.filter(
                    facility_class__facility_enrollment=(
                        attendee_enrollment.faction_enrollment.facility_enrollment
                    )
                ).select_related("facility_class", "period", "department")
            )
        else:
            self.fields["facility_class_enrollment"].queryset = (
                FacilityClassEnrollment.objects.select_related(
                    "facility_class", "period", "department"
                )
            )
        self._apply_form_control_class()

    def _selected_attendee_enrollment(self):
        if self.instance.pk and self.instance.attendee_enrollment_id:
            return self.instance.attendee_enrollment
        value = self.data.get("attendee_enrollment") if self.data else None
        if value:
            try:
                return AttendeeEnrollment.objects.select_related(
                    "faction_enrollment__facility_enrollment"
                ).get(pk=value)
            except (AttendeeEnrollment.DoesNotExist, ValueError, TypeError):
                return None
        value = self.initial.get("attendee_enrollment")
        if isinstance(value, AttendeeEnrollment):
            return value
        if value:
            try:
                return AttendeeEnrollment.objects.select_related(
                    "faction_enrollment__facility_enrollment"
                ).get(pk=value)
            except (AttendeeEnrollment.DoesNotExist, ValueError, TypeError):
                return None
        return None

    def _apply_form_control_class(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


AttendeeQuartersAssignmentForm = AttendeeEnrollmentForm
AttendeeClassAssignmentForm = AttendeeClassEnrollmentForm
