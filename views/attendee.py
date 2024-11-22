# enrollment/views/attendee.py

from django_tables2 import SingleTableView
from ..models.faction import AttendeeEnrollment
from ..tables.attendee import AttendeeEnrollmentTable
from django.contrib.auth import get_user_model

User = get_user_model()


class AttendeeEnrollmentIndexByAttendeeView(SingleTableView):
    model = AttendeeEnrollment
    table_class = AttendeeEnrollmentTable
    template_name = "attendee_enrollment/index.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        # Filter enrollments by attendee slug or pk
        attendee_slug = self.kwargs.get("slug")
        return AttendeeEnrollment.objects.filter(
            attendee__user__slug=attendee_slug
        ).select_related("attendee", "faction_enrollment", "quarters")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee_slug = self.kwargs.get("slug")
        context["attendee"] = User.objects.get(slug=attendee_slug)
        return context
