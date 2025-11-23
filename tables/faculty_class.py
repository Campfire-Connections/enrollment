# enrollment/tables/faculty_class.py

import django_tables2 as tables
from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty import FacultyEnrollment


class FacultyClassEnrollmentTable(OrganizationLabelMixin, BaseTable):
    faculty = tables.Column(accessor="faculty__name", verbose_name="Faculty")
    facility_class = tables.Column(
        accessor="facility_class__name", verbose_name="Facility Class"
    )
    period = tables.Column(accessor="period__name", verbose_name="Period")
    department = tables.Column(accessor="department__name", verbose_name="Department")
    organization_enrollment = tables.Column(
        accessor="organization_enrollment__name", verbose_name="Organization Enrollment"
    )
    max_enrollment = tables.Column(verbose_name="Max Enrollment")

    class Meta:
        model = FacilityClassEnrollment
        fields = (
            "faculty",
            "facility_class",
            "period",
            "department",
            "organization_enrollment",
            "max_enrollment",
        )
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = "faculty:class_enrollments"

    urls = {
        "add": {"kwargs": {"facility_class_slug": "facility_class__slug"}},
        "show": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "faculty_class_enrollment_slug": "slug",
            }
        },
        "edit": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "faculty_class_enrollment_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_class_slug": "facility_class__slug",
                "faculty_class_enrollment_slug": "slug",
            }
        },
    }
    available_actions = ["show", "edit", "delete"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassScheduleTable(BaseTable):
    session = tables.Column(
        accessor="facility_enrollment__name", verbose_name="Session"
    )
    facility = tables.Column(
        accessor="facility_enrollment__facility__name", verbose_name="Facility"
    )
    start_time = tables.DateColumn(
        accessor="facility_enrollment__start", verbose_name="Start Date"
    )
    end_time = tables.DateColumn(
        accessor="facility_enrollment__end", verbose_name="End Date"
    )

    class Meta:
        model = FacultyEnrollment
        fields = ["session", "facility", "start_time", "end_time"]
        attrs = {"class": "table table-striped table-bordered"}

    available_actions = []
