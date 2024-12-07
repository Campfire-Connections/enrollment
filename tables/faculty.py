# enrollment/tables/faculty.py

import django_tables2 as tables

from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable

from ..models.faculty import FacultyEnrollment


class FacultyEnrollmentTable(OrganizationLabelMixin, BaseTable):
    faculty = tables.Column(accessor="faculty.name", verbose_name="Faculty")
    facility_enrollment = tables.Column(
        accessor="facility_enrollment.name", verbose_name="Facility Enrollment"
    )
    start_date = tables.DateTimeColumn(format="M d, Y", verbose_name="Start Date")
    end_date = tables.DateTimeColumn(format="M d, Y", verbose_name="End Date")

    class Meta:
        model = FacultyEnrollment
        fields = ("faculty", "facility_enrollment", "start_date", "end_date")
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "faculty:enrollments"

    urls = {
        "add": {"kwargs": {"faculty_slug": "faculty__slug"}},
        "show": {
            "kwargs": {
                "faculty_slug": "faculty__slug",
                "faculty_enrollment_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "faculty_slug": "faculty__slug",
                "faculty_enrollment_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "faculty_slug": "faculty__slug",
                "faculty_enrollment_slug": "slug",
            }
        },
    }
    available_actions = ["show", "edit", "delete"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
