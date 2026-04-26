# enrollment/views/enrollment.py

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from core.views.base import (
    BaseListView,
    BaseDetailView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseTemplateView,
)
from core.mixins.views import LoginRequiredMixin

from ..models.enrollment import ActiveEnrollment
from ..services import ActiveEnrollmentService


class ActiveEnrollmentIndexView(BaseListView):
    model = ActiveEnrollment
    template_name = "active_enrollment/index.html"
    context_object_name = "active_enrollments"


class ActiveEnrollmentShowView(BaseDetailView):
    model = ActiveEnrollment
    template_name = "active_enrollment/show.html"
    context_object_name = "active_enrollment"


class ActiveEnrollmentCreateView(BaseCreateView):
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

    def form_valid(self, form):
        service = ActiveEnrollmentService(form.cleaned_data["user"])
        self.object = service.set_active(
            attendee_enrollment=form.cleaned_data.get("attendee_enrollment"),
            leader_enrollment=form.cleaned_data.get("leader_enrollment"),
            faction_enrollment=form.cleaned_data.get("faction_enrollment"),
            faculty_enrollment=form.cleaned_data.get("faculty_enrollment"),
            facility_enrollment=form.cleaned_data.get("facility_enrollment"),
        )
        return HttpResponseRedirect(self.get_success_url())


class ActiveEnrollmentUpdateView(BaseUpdateView):
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

    def form_valid(self, form):
        service = ActiveEnrollmentService(form.cleaned_data["user"])
        self.object = service.set_active(
            attendee_enrollment=form.cleaned_data.get("attendee_enrollment"),
            leader_enrollment=form.cleaned_data.get("leader_enrollment"),
            faction_enrollment=form.cleaned_data.get("faction_enrollment"),
            faculty_enrollment=form.cleaned_data.get("faculty_enrollment"),
            facility_enrollment=form.cleaned_data.get("facility_enrollment"),
        )
        return HttpResponseRedirect(self.get_success_url())


class ActiveEnrollmentDeleteView(BaseDeleteView):
    model = ActiveEnrollment
    template_name = "active_enrollment/confirm_delete.html"
    success_url = reverse_lazy("active_enrollment:index")


class MyScheduleView(LoginRequiredMixin, BaseTemplateView):
    template_name = "enrollment/my_schedule.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_enrollment = (
            ActiveEnrollment.objects.with_related()
            .filter(user=self.request.user)
            .first()
        )

        context["active_enrollment"] = active_enrollment
        if not active_enrollment:
            return context

        attendee_enrollment = active_enrollment.attendee_enrollment
        faculty_enrollment = active_enrollment.faculty_enrollment
        context["attendee_enrollment"] = attendee_enrollment
        context["leader_enrollment"] = active_enrollment.leader_enrollment
        context["faction_enrollment"] = active_enrollment.faction_enrollment
        context["faculty_enrollment"] = faculty_enrollment
        context["facility_enrollment"] = active_enrollment.facility_enrollment
        context["attendee_classes"] = (
            attendee_enrollment.class_enrollments.select_related(
                "facility_class_enrollment__facility_class",
                "facility_class_enrollment__period",
                "facility_class_enrollment__department",
            )
            if attendee_enrollment
            else []
        )
        context["faculty_classes"] = (
            faculty_enrollment.class_enrollments.select_related(
                "facility_class_enrollment__facility_class",
                "facility_class_enrollment__period",
                "facility_class_enrollment__department",
            )
            if faculty_enrollment
            else []
        )

        return context
