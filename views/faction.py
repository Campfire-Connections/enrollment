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

from faction.models.faction import Faction

from ..models.faction import FactionEnrollment
from ..models.leader import LeaderEnrollment
from ..models.attendee import AttendeeEnrollment
from ..models.attendee_class import AttendeeClassEnrollment
from ..models.facility import FacilityEnrollment
from ..forms.faction import FactionEnrollmentForm
from ..services import SchedulingService
from ..mixin import SchedulingServiceFormMixin


class FactionEnrollmentIndexView(ListView):
    model = FactionEnrollment
    template_name = "faction-enrollment/index.html"
    context_object_name = "faction_enrollments"

    def get_queryset(self):
        qs = FactionEnrollment.objects.with_related()
        slug = self.kwargs.get("slug")
        if slug:
            qs = qs.filter(faction__slug=slug)
        else:
            profile = getattr(self.request.user, "leaderprofile_profile", None)
            if profile and profile.faction_id:
                qs = qs.filter(faction_id=profile.faction_id)
        return qs


class FactionEnrollmentShowView(DetailView):
    model = FactionEnrollment
    template_name = "faction-enrollment/show.html"
    context_object_name = "faction_enrollment"

    def get_queryset(self):
        return FactionEnrollment.objects.with_related()


class FactionEnrollmentCreateView(SchedulingServiceFormMixin, CreateView):
    model = FactionEnrollment
    #fields = "__all__"
    template_name = "faction-enrollment/form.html"
    success_url = reverse_lazy("factions:enrollments:index")
    form_class = FactionEnrollmentForm
    service_class = SchedulingService
    service_method = "schedule_faction_enrollment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faction"] = self._get_faction()
        return context

    def _get_faction(self):
        return get_object_or_404(Faction, slug=self.kwargs.get("slug"))

    def get_service_kwargs(self, form):
        faction = self._get_faction()
        week = form.cleaned_data["week"]
        return {
            "faction": faction,
            "facility_enrollment": form.cleaned_data["facility_enrollment"],
            "week": week,
            "quarters": form.cleaned_data["quarters"],
            "start": week.start,
            "end": week.end,
            "name": form.instance.name or f"{faction.name} - {week.name}",
            "description": form.instance.description,
        }

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


class AttendeeEnrollmentCreateView(SchedulingServiceFormMixin, CreateView):
    model = AttendeeEnrollment
    fields = "__all__"
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")
    service_class = SchedulingService
    service_method = "schedule_attendee_enrollment"


class AttendeeEnrollmentUpdateView(SchedulingServiceFormMixin, UpdateView):
    model = AttendeeEnrollment
    fields = "__all__"
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")
    service_method = "schedule_attendee_enrollment"

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        kwargs = super().get_service_kwargs(form)
        kwargs["attendee_enrollment"] = self.object
        return kwargs


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


class AttendeeClassEnrollmentCreateView(SchedulingServiceFormMixin, CreateView):
    model = AttendeeClassEnrollment
    fields = "__all__"
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
    service_class = SchedulingService
    service_method = "assign_attendee_to_class"


class AttendeeClassEnrollmentUpdateView(SchedulingServiceFormMixin, UpdateView):
    model = AttendeeClassEnrollment
    fields = "__all__"
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
    service_method = "assign_attendee_to_class"

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        kwargs = super().get_service_kwargs(form)
        kwargs["attendee_class_enrollment"] = self.object
        return kwargs


class AttendeeClassEnrollmentDeleteView(DeleteView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
