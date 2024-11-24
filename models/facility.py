# enrollment/models/facility.py
"""Facility Enrollment Related Models."""

from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import models as mixins
from core.mixins import settings as stgs

from .temporal import AbstractTemporalHierarchy, Period
from .organization import OrganizationEnrollment


class FacilityEnrollment(AbstractTemporalHierarchy):
    """Facility Enrollment Model."""

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

class FacilityClassEnrollment(
    mixins.NameDescriptionMixin,
    mixins.TimestampMixin,
    mixins.SoftDeleteMixin,
    mixins.AuditMixin,
    mixins.SlugMixin,
    mixins.ActiveMixin,
    models.Model,
):
    """Facility Class Enrollment Model."""

    facility_class = models.ForeignKey("course.FacilityClass", on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    department = models.ForeignKey("facility.Department", on_delete=models.CASCADE)
    organization_enrollment = models.ForeignKey(
        OrganizationEnrollment, on_delete=models.CASCADE
    )
    max_enrollment = models.PositiveIntegerField(default=30)

    def clean(self):
        """Ensure enrollment does not exceed max."""
        super().clean()
        current_enrollment_count = FacilityClassEnrollment.objects.filter(
            facility_class=self.facility_class
        ).count()
        if current_enrollment_count >= self.max_enrollment:
            raise ValidationError("Max enrollment limit reached for this class.")

    class Meta:
        verbose_name = "Facility Class Enrollment"
        verbose_name_plural = "Facility Class Enrollments"
        ordering = ["facility_class__name", "period__start"]
        indexes = [models.Index(fields=["facility_class", "period"])]

    def __str__(self):
        return f"{self.facility_class} - {self.period} - {self.department}"


class FacultyEnrollment(models.Model):
    """Faculty Enrollment Model."""

    faculty = models.ForeignKey(
        "facility.Faculty",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Faculty",
    )
    facility_enrollment = models.ForeignKey(
        FacilityEnrollment,
        on_delete=models.CASCADE,
        related_name="faculty_enrollments",
        verbose_name="Facility Enrollment",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="faculty_enrollments",
        verbose_name="Quarters",
    )
    role = models.CharField(max_length=100, blank=True, null=True)  # New field

    class Meta:
        verbose_name = "Faculty Enrollment"
        verbose_name_plural = "Faculty Enrollments"
        ordering = ["faculty__last_name", "faculty__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "facility_enrollment", "quarters"],
                name="unique_faculty_enrollment",
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.faculty} - {self.facility_enrollment.facility.name}"


class FacultyClassEnrollment(models.Model):
    """Faculty Class Enrollment Model.

    Represents the enrollment of faculty in a specific class at a facility.
    """

    faculty = models.ForeignKey(
        "facility.Faculty",
        on_delete=models.CASCADE,
        related_name="class_enrollments",
        verbose_name="Faculty",
    )
    facility_class_enrollment = models.ForeignKey(
        FacilityClassEnrollment,
        on_delete=models.CASCADE,
        related_name="faculty_class_enrollments",
        null=True,
        blank=True,
        verbose_name="Facility Class Enrollment",
    )
    faculty_enrollment = models.ForeignKey(
        FacultyEnrollment,
        on_delete=models.CASCADE,
        related_name="class_enrollments",
        null=True,
        blank=True,
        verbose_name="Faculty Enrollment",
    )

    class Meta:
        """Metadata."""

        verbose_name = "Faculty Class Enrollment"
        verbose_name_plural = "Faculty Class Enrollments"
        ordering = ["faculty__last_name", "faculty__first_name"]

    def __str__(self):
        """String representation."""
        return f"{self.faculty} - {self.facility_class_enrollment}"
