# enrollment/models/attendee_class.py

from django.db import models


class AttendeeClassEnrollment(models.Model):
    """Attendee Class Enrollment Model.

    Represents the enrollment of an attendee in a specific class during an enrollment period.
    """
    attendee = models.ForeignKey(
        "faction.AttendeeProfile",
        on_delete=models.CASCADE,
        related_name="class_enrollments",
        verbose_name="Faculty",
    )
    attendee_enrollment = models.ForeignKey(
        "enrollment.AttendeeEnrollment",
        on_delete=models.CASCADE,
        related_name="class_enrollments",
        verbose_name="Attendee Enrollment",
        null=True,
        blank=True,
    )
    facility_class_enrollment = models.ForeignKey(
        "enrollment.FacilityClassEnrollment",
        on_delete=models.CASCADE,
        related_name="attendee_class_enrollments",
        verbose_name="Facility Class Enrollment",
        null=True,
        blank=True,
    )

    class Meta:
        """Metadata."""

        verbose_name = "Attendee Class Enrollment"
        verbose_name_plural = "Attendee Class Enrollments"
        ordering = [
            "attendee__user__last_name",
            "attendee__user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["attendee", "facility_class_enrollment"],
                condition=models.Q(facility_class_enrollment__isnull=False),
                name="unique_attendee_class_assignment",
                violation_error_message=(
                    "This enrollment conflicts with an existing assignment."
                ),
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.attendee} - {self.facility_class_enrollment}"
