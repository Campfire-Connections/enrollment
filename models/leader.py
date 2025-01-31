# enrollment/models/leader.py

from django.db import models

from .temporal import AbstractTemporalHierarchy

from ..querysets import LeaderEnrollmentQuerySet

class LeaderEnrollment(AbstractTemporalHierarchy):
    """Leader Enrollment Model."""

    leader = models.ForeignKey(
        "faction.LeaderProfile",
        on_delete=models.CASCADE,
        related_name="leader_enrollments",
        verbose_name="Leader",
    )
    faction_enrollment = models.ForeignKey(
        "enrollment.FactionEnrollment",
        on_delete=models.CASCADE,
        related_name="leader_enrollments",
        verbose_name="Faction Enrollment",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="leader_enrollments",
        verbose_name="Quarters",
    )
    role = models.CharField(max_length=100, blank=True, null=True)  # New field
    

    objects = LeaderEnrollmentQuerySet.as_manager()

    class Meta:
        verbose_name = "Leader Enrollment"
        verbose_name_plural = "Leader Enrollments"
        ordering = ["leader__user__last_name", "leader__user__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["leader", "faction_enrollment", "quarters"],
                name="unique_leader_enrollment",
            )
        ]

    def __str__(self):
        """String representation."""
        return f"{self.leader} - {self.faction_enrollment.faction.name}"
