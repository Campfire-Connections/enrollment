# enrollment/tables/leader.py

import django_tables2 as tables

from core.tables.base import BaseTable
from enrollment.models.leader import LeaderEnrollment


class LeaderEnrollmentTable(BaseTable):
    leader = tables.Column(accessor="faction.LeaderProfile", verbose_name="Leader")
    faction_enrollment = tables.Column(
        accessor="faction_enrollment.name",
        verbose_name="Faction Enrollment",
    )
    quarters = tables.Column(accessor="quarters.name", verbose_name="Quarters")
    role = tables.Column(accessor="role", verbose_name="Role")

    class Meta:
        model = LeaderEnrollment
        leader = model.leader
        template_name = "django_tables2/bootstrap4.html"
        fields = ("leader", "facility", "quarters", "week_name")
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "leaders:enrollments"
    urls = {
        "add": {
            "name": "leaders:enrollments:new",
            "kwargs": {"slug": "leader__slug"},
        },
        "show": {
            "name": "leaders:enrollments:show",
            "kwargs": {"slug": "leader__slug", "enrollment_slug": "slug"},
        },
        "edit": {
            "name": "leaders:enrollments:edit",
            "kwargs": {"slug": "leader__slug", "enrollment_slug": "slug"},
        },
        "delete": {
            "name": "leaders:enrollments:delete",
            "kwargs": {"slug": "leader__slug", "enrollment_slug": "slug"},
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_actions_column()
