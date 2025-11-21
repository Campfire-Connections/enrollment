# enrollment/views/faction.py

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

from faction.models.faction import Faction

from ..models.faction import FactionEnrollment
from ..models.leader import LeaderEnrollment
from ..models.attendee import AttendeeEnrollment
from ..models.attendee_class import AttendeeClassEnrollment
from ..models.facility import FacilityEnrollment
from ..forms.faction import FactionEnrollmentForm
from ..services import SchedulingService


class FactionEnrollmentIndexView(ListView):
    model = FactionEnrollment
    template_name = "faction-enrollment/index.html"
    context_object_name = "faction_enrollments"

    def get_queryset(self):
        return FactionEnrollment.objects.with_related()


class FactionEnrollmentShowView(DetailView):
    model = FactionEnrollment
    template_name = "faction-enrollment/show.html"
    context_object_name = "faction_enrollment"

    def get_queryset(self):
        return FactionEnrollment.objects.with_related()


class FactionEnrollmentCreateView(CreateView):
    model = FactionEnrollment
    #fields = "__all__"
    template_name = "faction-enrollment/form.html"
    success_url = reverse_lazy("factions:enrollments:index")
    form_class = FactionEnrollmentForm
    service_class = SchedulingService

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faction = get_object_or_404(Faction, slug=self.kwargs.get("slug"))
        context["faction"] = faction
        return context

    def form_valid(self, form):
        faction = get_object_or_404(Faction, slug=self.kwargs.get("slug"))
        service = self.service_class(user=self.request.user)
        week = form.cleaned_data["week"]
        try:
            self.object = service.schedule_faction_enrollment(
                faction=faction,
                facility_enrollment=form.cleaned_data["facility_enrollment"],
                week=week,
                quarters=form.cleaned_data["quarters"],
                start=week.start,
                end=week.end,
                name=form.instance.name or f"{faction.name} - {week.name}",
                description=form.instance.description,
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("factions:show", kwargs={"slug": self.object.faction.slug})

class FactionEnrollmentUpdateView(UpdateView):
    model = FactionEnrollment
    fields = "__all__"
    template_name = "faction-enrollment/form.html"
    success_url = reverse_lazy("faction:faction_enrollment_index")


class FactionEnrollmentDeleteView(DeleteView):
    model = FactionEnrollment
    template_name = "faction-enrollment/confirm_delete.html"
    success_url = reverse_lazy("faction:faction_enrollment_index")





class AttendeeEnrollmentIndexView(ListView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/index.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        return AttendeeEnrollment.objects.with_related()

class AttendeeEnrollmentIndexByAttendee(ListView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/index.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        return AttendeeEnrollment.objects.with_related()
    
class AttendeeEnrollmentShowView(DetailView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/show.html"
    context_object_name = "attendee_enrollment"


class AttendeeEnrollmentCreateView(CreateView):
    model = AttendeeEnrollment
    fields = "__all__"
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")
    service_class = SchedulingService

    def form_valid(self, form):
        service = self.service_class(user=self.request.user)
        try:
            self.object = service.schedule_attendee_enrollment(
                attendee=form.cleaned_data["attendee"],
                faction_enrollment=form.cleaned_data["faction_enrollment"],
                quarters=form.cleaned_data.get("quarters"),
                role=form.cleaned_data.get("role"),
                start=form.cleaned_data.get("start"),
                end=form.cleaned_data.get("end"),
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())


class AttendeeEnrollmentUpdateView(UpdateView):
    model = AttendeeEnrollment
    fields = "__all__"
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")


class AttendeeEnrollmentDeleteView(DeleteView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/confirm_delete.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")


class AttendeeClassEnrollmentIndexView(ListView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/index.html"
    context_object_name = "attendee_class_enrollments"


class AttendeeClassEnrollmentShowView(DetailView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/show.html"
    context_object_name = "attendee_class_enrollment"


class AttendeeClassEnrollmentCreateView(CreateView):
    model = AttendeeClassEnrollment
    fields = "__all__"
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
    service_class = SchedulingService

    def form_valid(self, form):
        service = self.service_class(user=self.request.user)
        try:
            self.object = service.assign_attendee_to_class(
                attendee=form.cleaned_data["attendee"],
                attendee_enrollment=form.cleaned_data.get("attendee_enrollment"),
                facility_class_enrollment=form.cleaned_data[
                    "facility_class_enrollment"
                ],
            )
        except ValidationError as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())


class AttendeeClassEnrollmentUpdateView(UpdateView):
    model = AttendeeClassEnrollment
    fields = "__all__"
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")


class AttendeeClassEnrollmentDeleteView(DeleteView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
