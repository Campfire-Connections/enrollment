# enrollment/models/attendee.py

from django.db import models

from .temporal import AbstractTemporalHierarchy
from ..querysets import AttendeeEnrollmentQuerySet

class AttendeeEnrollment(AbstractTemporalHierarchy):
    """Attendee Enrollment Model."""

    attendee = models.ForeignKey(
        "faction.AttendeeProfile",
        on_delete=models.CASCADE,
        related_name="attendee_enrollments",
        verbose_name="Attendee",
    )
    faction_enrollment = models.ForeignKey(
        "enrollment.FactionEnrollment",
        on_delete=models.CASCADE,
        related_name="attendee_enrollments",
        verbose_name="Faction Enrollment",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="attendee_enrollments",
        verbose_name="Quarters",
    )
    role = models.CharField(max_length=100, blank=True, null=True)  # New field
    
    @property
    def classes(self):
        return self.faction_enrollment.facility_classes.all()
    
    objects = AttendeeEnrollmentQuerySet.as_manager()

    class Meta:
        verbose_name = "Attendee Enrollment"
        verbose_name_plural = "Attendee Enrollments"
        ordering = ["attendee__user__last_name", "attendee__user__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["attendee", "faction_enrollment", "quarters"],
                name="unique_attendee_enrollment",
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.attendee} - {self.faction_enrollment.faction.name}"
