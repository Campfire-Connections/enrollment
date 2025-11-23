# enrollment/tables/facility.py

import django_tables2 as tables

from core.mixins.tables import OrganizationLabelMixin
from core.tables.base import BaseTable
from course.models.facility_class import FacilityClass

from ..models.facility import FacilityEnrollment

class FacilityEnrollmentTable(OrganizationLabelMixin, BaseTable):
    organization_enrollment = tables.Column(
        accessor="organization_enrollment__name", verbose_name="Organization Enrollment"
    )
    start = tables.DateTimeColumn(format="M d", verbose_name="Start Date")
    end = tables.DateTimeColumn(format="M d", verbose_name="End Date")

    class Meta:
        model = FacilityEnrollment
        fields = ("name", "organization_enrollment", "start", "end")

    url_namespace = "facilities:enrollments"

    urls = {
        "add": {"kwargs": {"facility_slug": "facility__slug"}},
        "show": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "slug",
            }
        },
        "manage": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "slug",
            },
            "icon": "list-check",
            "name": "facilities:enrollments:manage",
        },
        "edit": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "slug",
            }
        },
        "delete": {
            "kwargs": {
                "facility_slug": "facility__slug",
                "facility_enrollment_slug": "slug",
            }
        },
    }
    available_actions = ["show", "edit", "delete", "manage"]

    def getFacility(self, slug=False):
        facility = self.facility

        return facility.slug if slug else facility

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
