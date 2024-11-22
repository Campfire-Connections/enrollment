# enrollment/tables/attendee.py

import django_tables2 as tables

from ..models.faction import AttendeeEnrollment


class AttendeeEnrollmentTable(tables.Table):
    class Meta:
        model = AttendeeEnrollment
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "attendee",
            "faction_enrollment",
            "quarters",
            "start",
            "end",
        )
    url_namespace = "attendees:enrollments"