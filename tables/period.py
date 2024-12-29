# enrollment/tables/period.py

import django_tables2 as tables

from core.tables.base import BaseTable
from ..models.temporal import Period


class PeriodTable(BaseTable):
    """A Django table for displaying and managing enrollment periods.

    Provides a structured view of periods with columns for week name, start time, and end time,
    including dynamic URL routing for various period-related actions.

    Attributes:
        week_name: A column displaying the associated week's name.
        start: A column showing the period's start time.
        end: A column showing the period's end time.

    Metadata:
        Model: Period
        Template: Bootstrap5
        Default Ordering: By week name
        URL Namespace: facilities:enrollments:weeks:periods
    """

    week_name = tables.Column(
        accessor="week.name",
        verbose_name="Week",
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


class PeriodsByWeekTable(PeriodTable):
    """A specialized table for displaying periods within a specific week.

    Extends the PeriodTable to provide a focused view of periods, with a customized set of
    displayed fields.

    Inherits:
        PeriodTable: The base table for period-related information.
    """

    class Meta(PeriodTable.Meta):
        fields = ["name", "start", "end"]

    def __init__(self, *args, **kwargs):
        """Initializes the table with a subset of columns defined in the Meta fields.

        Overrides the default initialization to restrict the table to only the columns specified
        in the Meta fields.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        super().__init__(*args, **kwargs)
        self.base_columns = {key: self.base_columns[key] for key in self.Meta.fields}
