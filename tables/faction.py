# enrollment/tables/faction.py

import django_tables2 as tables
from core.tables.base import BaseTable
from ..models.faction import FactionEnrollment


class FactionEnrollmentTable(BaseTable):
    available_actions = ["show", "edit", "delete"]
    facility = tables.Column(
        accessor="week__facility_enrollment__facility", verbose_name="Facility"
    )
    week_name = tables.Column(
        accessor="week__name",
        verbose_name="Week",
    )
    class Meta:
        model = FactionEnrollment
        faction = model.faction
        template_name = "django_tables2/bootstrap4.html"
        fields = ("faction", "facility", "quarters", "week_name")
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "factions:enrollments"
    urls = {
        "add": {
            "name": "factions:enrollments:new",
            "kwargs": {"slug": "faction__slug"},
        },
        "show": {
            "name": "factions:enrollments:show",
            "kwargs": {"slug": "faction__slug", "enrollment_slug": "slug"},
        },
        "edit": {
            "name": "factions:enrollments:edit",
            "kwargs": {"slug": "faction__slug", "enrollment_slug": "slug"},
        },
        "delete": {
            "name": "factions:enrollments:delete",
            "kwargs": {"slug": "faction__slug", "enrollment_slug": "slug"},
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_actions_column()
