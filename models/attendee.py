# enrollment/models/attendee.py

from django.db import models
from django.core.exceptions import ValidationError

from .temporal import AbstractTemporalHierarchy
from ..querysets import AttendeeEnrollmentQuerySet
from django.apps import apps

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

    def clean(self):
        super().clean()
        faction = self.faction_enrollment
        quarters = self.quarters or getattr(faction, "quarters", None)
        if not faction or not quarters:
            raise ValidationError("Attendee enrollments require faction and quarters.")
        capacity = quarters.capacity or 0
        if capacity > 0:
            attendee_count = (
                AttendeeEnrollment.objects.filter(
                    faction_enrollment=faction, quarters=quarters
                )
                .exclude(pk=self.pk)
                .count()
            )
            LeaderEnrollment = apps.get_model("enrollment", "LeaderEnrollment")
            leader_count = LeaderEnrollment.objects.filter(
                faction_enrollment=faction, quarters=quarters
            ).count()
            if attendee_count + leader_count >= capacity:
                raise ValidationError("Selected quarters are already full.")

    def save(self, *args, **kwargs):
        if self.faction_enrollment and not self.start:
            self.start = self.faction_enrollment.start
        if self.faction_enrollment and not self.end:
            self.end = self.faction_enrollment.end
        super().save(*args, **kwargs)
