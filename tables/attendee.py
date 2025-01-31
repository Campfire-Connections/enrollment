# enrollment/tables/attendee.py

import django_tables2 as tables

from ..models.attendee import AttendeeEnrollment
from ..models.attendee_class import AttendeeClassEnrollment


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
    
class AttendeeScheduleTable(AttendeeEnrollmentTable):
    class Meta:
        model = AttendeeClassEnrollment
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "attendee",
            "attendee_enrollment",
            "facility_class_enrollment",
        )
    url_namespace = "attendees:enrollments"
        