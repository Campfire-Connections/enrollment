# enrollment/models/facility.py
"""Facility Enrollment Related Models."""

from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import models as mixins
from core.mixins import settings as stgs

from .temporal import AbstractTemporalHierarchy
from .organization import OrganizationEnrollment


class FacilityEnrollment(AbstractTemporalHierarchy):
    """Facility Enrollment Model."""

    start = models.DateField(verbose_name="Start Date")
    end = models.DateField(verbose_name="End Date")
    organization_enrollment = models.ForeignKey(
        OrganizationEnrollment,
        on_delete=models.CASCADE,
        related_name="facility_enrollments",
        verbose_name="Organization Enrollment",
    )
    facility = models.ForeignKey(
        "facility.Facility",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Facility",
    )
    status = models.CharField(
        max_length=10,
        choices=[("active", "Active"), ("expired", "Expired")],
        default="active",
    )

    class Meta:
        verbose_name = "Facility Enrollment"
        verbose_name_plural = "Facility Enrollments"
        ordering = ["start"]
        constraints = [
            models.UniqueConstraint(
                fields=["facility", "start", "end"], name="unique_facility_enrollment"
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.facility.name} Enrollment ({self.start} - {self.end})"

    def clean(self):
        """Ensure that the facility enrollment period is within the organization enrollment period."""
        super().clean()
        if self.start and self.end:
            org_enroll = self.organization_enrollment
            if self.start < org_enroll.start or self.end > org_enroll.end:
                raise ValidationError(
                    "Facility enrollment period must be within the organization enrollment period."
                )
