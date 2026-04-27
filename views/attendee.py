# enrollment/views/attendee.py

from core.views.base import BaseTableListView

from ..models.attendee import AttendeeEnrollment
from ..tables.attendee import AttendeeEnrollmentTable
from ..selectors import attendee_enrollments_for_attendee_slug, get_attendee_by_slug


class AttendeeEnrollmentIndexByAttendeeView(BaseTableListView):
    """
    List all enrollments for a given attendee, rendered as a django-tables2 table.
    """

    model = AttendeeEnrollment
    table_class = AttendeeEnrollmentTable
    template_name = "attendee_enrollment/index.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        return attendee_enrollments_for_attendee_slug(self.kwargs.get("slug"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attendee_slug = self.kwargs.get("slug")
        context["attendee"] = get_attendee_by_slug(attendee_slug)
        return context
