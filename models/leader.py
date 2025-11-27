# enrollment/models/leader.py

from django.db import models
from django.core.exceptions import ValidationError
from django.apps import apps

from .temporal import AbstractTemporalHierarchy

from ..querysets import LeaderEnrollmentQuerySet
from enrollment.cache_keys import invalidate_quarters_usage_cache

class LeaderEnrollment(AbstractTemporalHierarchy):
    """Leader Enrollment Model."""

    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
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
        """Return display string for admin and logs."""
        return f"{self.leader} - {self.faction_enrollment.faction.name}"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        invalidate_quarters_usage_cache(
            getattr(self.faction_enrollment, "id", None),
            getattr(self.quarters, "id", None),
        )
        return result

    def delete(self, *args, **kwargs):
        faction_id = getattr(self.faction_enrollment, "id", None)
        quarters_id = getattr(self.quarters, "id", None)
        result = super().delete(*args, **kwargs)
        invalidate_quarters_usage_cache(faction_id, quarters_id)
        return result

    def clean(self):
        super().clean()
        faction = self.faction_enrollment
        quarters = self.quarters or getattr(faction, "quarters", None)
        if not faction or not quarters:
            raise ValidationError("Leader enrollments require faction and quarters.")
        capacity = quarters.capacity or 0
        if capacity > 0:
            AttendeeEnrollment = apps.get_model("enrollment", "AttendeeEnrollment")
            attendee_count = AttendeeEnrollment.objects.filter(
                faction_enrollment=faction, quarters=quarters
            ).count()
            leader_count = (
                LeaderEnrollment.objects.filter(
                    faction_enrollment=faction, quarters=quarters
                )
                .exclude(pk=self.pk)
                .count()
            )
            if attendee_count + leader_count >= capacity:
                raise ValidationError("Selected quarters are already full.")

    def save(self, *args, **kwargs):
        if self.faction_enrollment and not self.start:
            self.start = self.faction_enrollment.start
        if self.faction_enrollment and not self.end:
            self.end = self.faction_enrollment.end
        super().save(*args, **kwargs)
