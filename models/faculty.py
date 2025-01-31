# enrollment/models/faculty.py

from django.db import models

from .temporal import AbstractTemporalHierarchy

from ..querysets import FacultyEnrollmentQuerySet

class FacultyEnrollment(AbstractTemporalHierarchy):
    """Faculty Enrollment Model."""

    faculty = models.ForeignKey(
        "facility.FacultyProfile",
        on_delete=models.CASCADE,
        related_name="faculty_enrollments",
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
    
    @property
    def classes(self):
        return self.facility_enrollment.facility_classes.all()
    
    objects = FacultyEnrollmentQuerySet.as_manager()

    class Meta:
        verbose_name = "Faculty Enrollment"
        verbose_name_plural = "Faculty Enrollments"
        ordering = ["faculty__user__last_name", "faculty__user__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "facility_enrollment", "quarters"],
                name="unique_faculty_enrollment",
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.faculty} - {self.facility_enrollment.facility.name}"
