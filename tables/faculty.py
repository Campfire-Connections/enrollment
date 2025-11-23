# enrollment/tables/faculty.py

import django_tables2 as tables

from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable

from ..models.faculty import FacultyEnrollment


class FacultyEnrollmentTable(OrganizationLabelMixin, BaseTable):
    """A Django table for displaying and managing faculty enrollment details.

    Provides a comprehensive view of faculty enrollments with columns for faculty name, facility
    enrollment, quarters, start date, and end date, including dynamic URL routing for various
    enrollment-related actions.

    Attributes:
        faculty: A column showing the faculty member's name.
        facility_enrollment: A column displaying the associated facility enrollment name.
        quarters: A column showing the faculty's assigned quarters.
        start_date: A column indicating the enrollment start date.
        end_date: A column indicating the enrollment end date.

    Metadata:
        Model: FacultyEnrollment
        URL Namespace: faculty:enrollments
        Available Actions: Show, Edit, Delete
    """

    faculty = tables.Column(accessor="faculty__name", verbose_name="Faculty")
    facility_enrollment = tables.Column(
        accessor="facility_enrollment__name", verbose_name="Facility Enrollment"
    )
    quarters = tables.Column(accessor="quarters__name", verbose_name="Faculty Quarters")
    start_date = tables.DateTimeColumn(format="M d, Y", verbose_name="Start Date")
    end_date = tables.DateTimeColumn(format="M d, Y", verbose_name="End Date")

    class Meta:
        model = FacultyEnrollment
        fields = (
            "faculty",
            "facility_enrollment",
            "quarters",
            "start_date",
            "end_date",
        )
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


class FacultyEnrollmentByFacilityEnrollmentTable(FacultyEnrollmentTable):
    """A specialized table for displaying faculty enrollments within a specific facility enrollment.

    Extends the FacultyEnrollmentTable to provide a focused view of faculty enrollments, with a
    customized set of displayed fields.

    Inherits:
        FacultyEnrollmentTable: The base table for faculty enrollment-related information.
    """

    last_name = tables.Column(accessor="faculty__user__last_name", verbose_name="Last Name")
    first_name = tables.Column(accessor="faculty__user__first_name", verbose_name="First Name")
    faculty = None

    class Meta(FacultyEnrollmentTable.Meta):
        fields = ("last_name", "first_name", "start_date", "end_date", "quarters")
        
