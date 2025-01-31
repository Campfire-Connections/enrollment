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


class FactionEnrollmentIndexView(ListView):
    model = FactionEnrollment
    template_name = "faction-enrollment/index.html"
    context_object_name = "faction_enrollments"


class FactionEnrollmentShowView(DetailView):
    model = FactionEnrollment
    template_name = "faction-enrollment/show.html"
    context_object_name = "faction_enrollment"


class FactionEnrollmentCreateView(CreateView):
    model = FactionEnrollment
    #fields = "__all__"
    template_name = "faction-enrollment/form.html"
    success_url = reverse_lazy("factions:enrollments:index")
    form_class = FactionEnrollmentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faction = get_object_or_404(Faction, slug=self.kwargs.get("slug"))
        context["faction"] = faction
        return context

    def form_valid(self, form):
        faction = get_object_or_404(Faction, slug=self.kwargs.get("slug"))
        form.instance.faction = faction  # Associate the faction with the enrollment
        return super().form_valid(form)

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

class AttendeeEnrollmentIndexByAttendee(ListView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/index.html"
    context_object_name = "attendee_enrollments"
    
class AttendeeEnrollmentShowView(DetailView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/show.html"
    context_object_name = "attendee_enrollment"


class AttendeeEnrollmentCreateView(CreateView):
    model = AttendeeEnrollment
    fields = "__all__"
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_enrollment_index")


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


class AttendeeClassEnrollmentUpdateView(UpdateView):
    model = AttendeeClassEnrollment
    fields = "__all__"
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")


class AttendeeClassEnrollmentDeleteView(DeleteView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("faction:attendee_class_enrollment_index")
