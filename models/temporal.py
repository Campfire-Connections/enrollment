# enrollment/models/temporal.py
"""Temporal Related Models."""

from django.db import models
from django.core.exceptions import ValidationError

from core.mixins import models as mixins


class AbstractTemporalHierarchy(
    mixins.NameDescriptionMixin,
    mixins.TimestampMixin,
    mixins.SoftDeleteMixin,
    mixins.AuditMixin,
    mixins.SlugMixin,
    mixins.ActiveMixin,
    models.Model,
):
    """
    Abstract Temporal Hierarchy Model.

    This abstract model provides a base for entities with time-related attributes.
    """

    class Meta:
        """Metadata."""

        abstract = True
        ordering = ["start"]
        verbose_name = "Temporal Hierarchy"
        verbose_name_plural = "Temporal Hierarchies"

    def clean(self):
        """Ensure that the start is before the end."""
        super().clean()
        if self.start and self.end and self.start > self.end:
            raise ValidationError("The start cannot be later than the end.")

    def __str__(self):
        """String representation."""
        return f"{self.name} ({self.start} - {self.end})"


class Week(AbstractTemporalHierarchy):
    """
    Week Model.

    Represents a week associated with a specific facility enrollment.
    """

    start = models.DateField(verbose_name="Start Date")
    end = models.DateField(verbose_name="End Date")
    facility_enrollment = models.ForeignKey(
        "FacilityEnrollment",
        on_delete=models.CASCADE,
        related_name="weeks",
        verbose_name="Facility Enrollment",
    )

    context_field = "facility_enrollment"

    class Meta:
        """Metadata."""

        verbose_name = "Week"
        verbose_name_plural = "Weeks"
        ordering = ["start"]
        unique_together = ("slug", "facility_enrollment")

    def get_periods(self):
        """Return all periods associated with this week."""
        return self.periods.all()

    def __str__(self):
        """String representation."""
        return f"Week: {self.name} ({self.start} - {self.end})"


class Period(AbstractTemporalHierarchy):
    """
    Period Model.

    Represents a period within a specific week.
    """

    start = models.TimeField(verbose_name="Start Time")
    end = models.TimeField(verbose_name="End Time")
    week = models.ForeignKey(
        Week, on_delete=models.CASCADE, related_name="periods", verbose_name="Week"
    )

    context_field = "week"

    class Meta:
        """Metadata."""

        verbose_name = "Period"
        verbose_name_plural = "Periods"
        ordering = ["start"]
        unique_together = ("slug", "week")

    def __str__(self):
        """String representation."""
        return f"Period: {self.name} ({self.start} - {self.end})"

    def get_week_name(self):
        """Return the name of the associated week."""
        return self.week.name
