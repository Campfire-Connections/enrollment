# enrollment/tables/week.py

import django_tables2 as tables

from core.tables.base import BaseTable
from ..models.temporal import Week


class WeekTable(BaseTable):
    """A Django table for displaying and managing enrollment weeks.

    Provides a comprehensive view of weeks with columns for name, start date, end date, and
    associated facility enrollment, including dynamic URL routing for various week-related actions.

    Attributes:
        start: A column showing the week's start date.
        end: A column showing the week's end date.
        facility_enrollment: A column displaying the associated facility enrollment name.

    Metadata:
        Model: Week
        Default Ordering: By week name
        Available Actions: Show, Edit, Delete, Manage
        URL Namespace: facilities:enrollments:weeks
    """

    start = tables.DateTimeColumn(format="M d", verbose_name="Start Date")
    end = tables.DateTimeColumn(format="M d", verbose_name="End Date")
    facility_enrollment = tables.Column(
        accessor="facility_enrollment.name", verbose_name="Facility Enrollment"
    )

    class Meta:
        model = Week
        fields = ["name", "start", "end", "facility_enrollment"]
        order_by = "name"

    available_actions = ["show", "edit", "delete", "manage"]
    url_namespace = "facilities:enrollments:weeks"
    urls = {
        "add": {
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
            }
        },
        "show": {
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
                "week_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
                "week_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
                "week_slug": "slug",
            }
        },
        "manage": {
            "name": "facilities:enrollments:weeks:manage",
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
                "week_slug": "slug",
            },
        },
    }


class WeekByFacilityEnrollmentTable(WeekTable):
    """A specialized table for displaying weeks within a specific facility enrollment.

    Extends the WeekTable to provide a focused view of weeks, with a customized set of displayed
    fields.

    Inherits:
        WeekTable: The base table for week-related information.
    """

    class Meta(WeekTable.Meta):
        fields = ["name", "start", "end"]
