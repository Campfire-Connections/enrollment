# enrollment/models/faculty.py

from django.db import models


class FacultyEnrollment(models.Model):
    """Faculty Enrollment Model."""

    faculty = models.ForeignKey(
        "facility.Faculty",
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Faculty",
    )
    facility_enrollment = models.ForeignKey(
        "enrollment.FacilityEnrollment",
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
