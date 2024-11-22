# enrollment/views/enrollment.py

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy

from ..models.enrollment import ActiveEnrollment


class ActiveEnrollmentIndexView(ListView):
    model = ActiveEnrollment
    template_name = "active_enrollment/index.html"
    context_object_name = "active_enrollments"


class ActiveEnrollmentShowView(DetailView):
    model = ActiveEnrollment
    template_name = "active_enrollment/show.html"
    context_object_name = "active_enrollment"


class ActiveEnrollmentCreateView(CreateView):
    model = ActiveEnrollment
    fields = [
        "user",
        "attendee_enrollment",
        "leader_enrollment",
        "faction_enrollment",
        "faculty_enrollment",
        "facility_enrollment",
    ]
    template_name = "active_enrollment/form.html"
    success_url = reverse_lazy("active_enrollment:index")


class ActiveEnrollmentUpdateView(UpdateView):
    model = ActiveEnrollment
    fields = [
        "user",
        "attendee_enrollment",
        "leader_enrollment",
        "faction_enrollment",
        "faculty_enrollment",
        "facility_enrollment",
    ]
    template_name = "active_enrollment/form.html"
    success_url = reverse_lazy("active_enrollment:index")


class ActiveEnrollmentDeleteView(DeleteView):
    model = ActiveEnrollment
    template_name = "active_enrollment/confirm_delete.html"
    success_url = reverse_lazy("active_enrollment:index")


class MyScheduleView(LoginRequiredMixin, TemplateView):
    template_name = "enrollment/my_schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the active enrollment for the current user
        active_enrollment = get_object_or_404(ActiveEnrollment, user=self.request.user)

        # Add active enrollment to the context
        context["active_enrollment"] = active_enrollment

        # You can add additional related information like classes, periods, etc.
        # Example:
        context["attendee_enrollment"] = active_enrollment.attendee_enrollment
        context["leader_enrollment"] = active_enrollment.leader_enrollment
        context["faction_enrollment"] = active_enrollment.faction_enrollment
        context["faculty_enrollment"] = active_enrollment.faculty_enrollment
        context["facility_enrollment"] = active_enrollment.facility_enrollment

        return context
