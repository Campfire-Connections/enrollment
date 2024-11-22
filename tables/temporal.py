# enrollment/tables/temporal.py

import django_tables2 as tables

from pages.tables.base import BaseTable
from ..models.temporal import Week, Period


class WeekTable(BaseTable):
    """Table definition for the Week model."""
    start = tables.DateTimeColumn(format="M d", verbose_name="Start Date")
    end = tables.DateTimeColumn(format="M d", verbose_name="End Date")
    facility_enrollment = tables.Column(
        accessor="facility_enrollment.name", verbose_name="Facility Enrollment"
    )

    class Meta:
        model = Week
        fields = ["name", "start", "end", "facility_enrollment"]
        order_by = "name"

    available_actions = ['show', 'edit', 'delete','manage']
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
            "kwargs": {
                "facility_slug": "facility_enrollment__facility__slug",
                "facility_enrollment_slug": "facility_enrollment__slug",
                "week_slug": "slug",
            },
        }
    }


class PeriodTable(tables.Table):
    """Table definition for the Period model."""

    week_name = tables.Column(
        accessor="get_week_name",
        verbose_name="Week Name",
    )
    start = tables.DateTimeColumn(format="h:i a", verbose_name="Start Time")
    end = tables.DateTimeColumn(format="h:i a", verbose_name="End Time")

    class Meta:
        model = Period
        template_name = "django_tables2/bootstrap5.html"
        fields = ["name", "start", "end", "week_name"]
        order_by = "week_name"

    url_namespace = "facilities:enrollments:weeks:periods"
    urls = {
        "add": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "week__facility_enrollment__slug",
                "week_slug": "week__slug",
            }
        },
        "show": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "week__facility_enrollment__slug",
                "week_slug": "week__slug",
                "period_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "week__facility_enrollment__slug",
                "week_slug": "week__slug",
                "period_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "week__facility_enrollment__slug",
                "week_slug": "week__slug",
                "period_slug": "slug",
            }
        },
    }
