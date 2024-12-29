# enrollment/models/faculty_class.py

from django.db import models


class FacultyClassEnrollment(models.Model):
    """Faculty Class Enrollment Model.

    Represents the enrollment of faculty in a specific class at a facility.
    """

    faculty = models.ForeignKey(
        "facility.FacultyProfile",
        on_delete=models.CASCADE,
        related_name="class_enrollments",
        verbose_name="Faculty",
    )
    facility_class_enrollment = models.ForeignKey(
        "enrollment.FacilityClassEnrollment",
        on_delete=models.CASCADE,
        related_name="faculty_class_enrollments",
        null=True,
        blank=True,
        verbose_name="Facility Class Enrollment",
    )
    faculty_enrollment = models.ForeignKey(
        "enrollment.FacultyEnrollment",
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
        ordering = ["faculty__user__last_name", "faculty__user__first_name"]

    def __str__(self):
        """String representation."""
        return f"{self.faculty} - {self.facility_class_enrollment}"
