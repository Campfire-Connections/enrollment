# enrollment/models/attendee_class.py

from django.db import models, transaction

from .availability import FacilityClassAvailability

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

    @transaction.atomic
    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = (
                AttendeeClassEnrollment.objects.only("facility_class_enrollment")
                .select_related("facility_class_enrollment")
                .get(pk=self.pk)
            )
        result = super().save(*args, **kwargs)
        self._sync_class_reservation(previous)
        return result

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self._release_current_slot()
        return super().delete(*args, **kwargs)

    def _sync_class_reservation(self, previous):
        if not previous:
            self._reserve_current_slot()
            return
        if previous.facility_class_enrollment_id != self.facility_class_enrollment_id:
            self._release_slot(previous.facility_class_enrollment)
            self._reserve_current_slot()

    def _reserve_current_slot(self):
        if not self.facility_class_enrollment_id:
            return
        availability = FacilityClassAvailability.for_enrollment(
            self.facility_class_enrollment
        )
        availability.reserve()

    def _release_current_slot(self):
        if not self.facility_class_enrollment_id:
            return
        self._release_slot(self.facility_class_enrollment)

    def _release_slot(self, facility_class_enrollment):
        try:
            availability = facility_class_enrollment.availability
        except FacilityClassAvailability.DoesNotExist:
            return
        availability.release()

    def __str__(self):
        """String representation."""
        return f"{self.attendee} - {self.facility_class_enrollment}"
