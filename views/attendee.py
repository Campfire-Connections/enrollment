# enrollment/views/attendee.py

from django.contrib.auth import get_user_model

from core.views.base import BaseTableListView

from ..models.attendee import AttendeeEnrollment
from ..tables.attendee import AttendeeEnrollmentTable

User = get_user_model()


class AttendeeEnrollmentIndexByAttendeeView(BaseTableListView):
    """
    List all enrollments for a given attendee, rendered as a django-tables2 table.
    """

    model = AttendeeEnrollment
    table_class = AttendeeEnrollmentTable
    template_name = "attendee_enrollment/index.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        attendee_slug = self.kwargs.get("slug")
        return (
            AttendeeEnrollment.objects.filter(attendee__user__slug=attendee_slug)
            .select_related("attendee", "faction_enrollment", "quarters")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee_slug = self.kwargs.get("slug")
        context["attendee"] = User.objects.get(slug=attendee_slug)
        return context
