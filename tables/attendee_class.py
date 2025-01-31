# enrollment/tables/attendee_class.py

import django_tables2 as tables

from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment

class AttendeeClassEnrollmentTable(OrganizationLabelMixin, BaseTable):
    attendee = tables.Column(accessor="attendee.name", verbose_name="Attendee")
    facility_class_enrollment = tables.Column(
        accessor="facility_class.name", verbose_name="Facility Class"
    )
    period = tables.Column(accessor="period.name", verbose_name="Period")
    department = tables.Column(accessor="department.name", verbose_name="Department")
    attendee_enrollment = tables.Column(
        accessor="attendee_enrollment.name", verbose_name="Organization Enrollment"
    )
    
    class Meta:
        model = AttendeeClassEnrollment
        fields = (
            "attendee",
            "facility_class_enrollment",
            "period",
            "department",
            "attendee_enrollment",
        )
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "factions:attendees:class_enrollments"

    urls = {
        "add": {"kwargs": {"facility_class_slug": "facility_class__slug"}},
        "show": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
    }
    available_actions = ["show", "edit", "delete"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassScheduleTable(BaseTable):
    class_name = tables.Column(
        accessor="facility_class.name", verbose_name="Class Name"
    )
    start_time = tables.DateTimeColumn(
        accessor="period.start", verbose_name="Start Time"
    )
    end_time = tables.DateTimeColumn(accessor="period.end", verbose_name="End Time")

    class Meta:
        model = FacilityClassEnrollment

        fields = ["class_name", "start_time", "end_time"]
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "attendees:enrollments:classes"

    urls = {
        "add": {"kwargs": {"facility_class_slug": "facility_class__slug"}},
        "show": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "attendee_class_enrollment_slug": "slug",
            }
        },
    }
    available_actions = ["show", "edit", "delete"]
