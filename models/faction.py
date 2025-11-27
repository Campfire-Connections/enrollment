# enrollment/models/faction.py
"""Faction Enrollment Related Models."""

from django.db import models, transaction
from django.core.exceptions import ValidationError

from core.mixins import models as mixins

# from core.mixins import settings as stgs

from .temporal import AbstractTemporalHierarchy, Week
from .facility_class import FacilityClassEnrollment
from .availability import QuartersWeekAvailability
from ..managers import (
    FactionEnrollmentManager,
    LeaderEnrollmentManager,
    AttendeeEnrollmentManager,
)
from enrollment.cache_keys import invalidate_quarters_usage_cache


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

    @transaction.atomic
    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = (
                FactionEnrollment.objects.select_related(
                    "facility_enrollment", "week", "quarters"
                )
                .only("facility_enrollment", "week", "quarters")
                .get(pk=self.pk)
            )
        result = super().save(*args, **kwargs)
        self._sync_quarters_reservation(previous)
        invalidate_quarters_usage_cache(
            getattr(self, "id", None),
            getattr(self, "quarters_id", None),
        )
        return result

    @transaction.atomic
    def delete(self, *args, **kwargs):
        faction_id = getattr(self, "id", None)
        quarters_id = getattr(self, "quarters_id", None)
        self._release_current_quarters()
        result = super().delete(*args, **kwargs)
        invalidate_quarters_usage_cache(faction_id, quarters_id)
        return result

    def _sync_quarters_reservation(self, previous):
        changed = (
            previous
            and (
                previous.quarters_id != self.quarters_id
                or previous.week_id != self.week_id
            )
        )
        if changed:
            previous._release_current_quarters()
        self._reserve_current_quarters()

    def _availability_filter(self, quarters=None, week=None):
        quarters = quarters or self.quarters
        week = week or self.week
        if not quarters or not week:
            return None
        return {
            "facility_enrollment": self.facility_enrollment,
            "week": week,
            "quarters": quarters,
        }

    def _reserve_current_quarters(self):
        lookup = self._availability_filter()
        if not lookup:
            return
        availability, _ = QuartersWeekAvailability.objects.get_or_create(
            defaults={"capacity": self.quarters.capacity},
            **lookup,
        )
        availability.reserve_full()

    def _release_current_quarters(self):
        lookup = self._availability_filter()
        if not lookup:
            return
        try:
            availability = QuartersWeekAvailability.objects.get(**lookup)
        except QuartersWeekAvailability.DoesNotExist:
            return
        availability.release_full()
