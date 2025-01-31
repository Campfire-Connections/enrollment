# enrollment/models/faction.py
"""Faction Enrollment Related Models."""

from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import models as mixins

# from core.mixins import settings as stgs

from .temporal import AbstractTemporalHierarchy, Week
from .facility_class import FacilityClassEnrollment
from ..managers import (
    FactionEnrollmentManager,
    LeaderEnrollmentManager,
    AttendeeEnrollmentManager,
)


class FactionEnrollment(AbstractTemporalHierarchy):
    """Faction Enrollment Model.

    Represents an enrollment period for a specific faction during a week.
    """

    facility_enrollment = models.ForeignKey(
        "FacilityEnrollment",
        on_delete=models.CASCADE,
        related_name="faction_enrollments",
        verbose_name="Facility Enrollment",
    )
    start = models.DateField(verbose_name="Start Date")
    end = models.DateField(verbose_name="End Date")
    faction = models.ForeignKey(
        "faction.Faction",
        on_delete=models.CASCADE,
        related_name="faction_enrollments",
        verbose_name="Faction",
    )
    week = models.ForeignKey(
        Week,
        on_delete=models.CASCADE,
        related_name="faction_enrollments",
        verbose_name="Week",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="faction_enrollments",
        verbose_name="Quarters",
    )

    objects = FactionEnrollmentManager()

    class Meta:
        """Metadata."""

        verbose_name = "Faction Enrollment"
        verbose_name_plural = "Faction Enrollments"
        ordering = ["start"]

    def __str__(self):
        """String representation."""
        return f"{self.faction.name} - {self.week}"

    def clean(self):
        """Ensure the week is within the temporal range."""
        super().clean()
        if (
            self.start
            and self.end
            and (self.week.start < self.start or self.week.end > self.end)
        ):
            raise ValidationError("Week dates must fall within the enrollment period.")

