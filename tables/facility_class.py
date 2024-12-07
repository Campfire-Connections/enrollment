# enrollment/tables/facility_class.py

import django_tables2 as tables

from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable

from ..models.facility_class import FacilityClassEnrollment


class FacilityClassEnrollmentTable(OrganizationLabelMixin, BaseTable):
    """Table for Facility Class Enrollments."""

    facility_class = tables.Column(
        verbose_name="Facility Class", accessor="course.facility_class.name"
    )
    period = tables.Column(verbose_name="Period", accessor="period.name")
    department = tables.Column(verbose_name="Department", accessor="department.name")
    organization_enrollment = tables.Column(
        verbose_name="Organization Enrollment", accessor="organization_enrollment.name"
    )
    max_enrollment = tables.Column(verbose_name="Max Enrollment")
    actions = tables.TemplateColumn(
        template_name="facility_class_enrollment/actions_column.html",
        verbose_name="Actions",
        orderable=False,
    )

    class Meta:
        model = FacilityClassEnrollment
        fields = (
            "facility_class",
            "period",
            "department",
            "organization_enrollment",
            "max_enrollment",
        )

    url_namespace = "facilities:enrollments:classes"

    available_actions = ["show", "edit", "delete"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
