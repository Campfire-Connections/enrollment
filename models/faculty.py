# enrollment/models/faculty.py

from django.db import models, transaction
from django.core.exceptions import ValidationError

from .temporal import AbstractTemporalHierarchy

from ..querysets import FacultyEnrollmentQuerySet
from .availability import FacultyQuartersAvailability

class FacultyEnrollment(AbstractTemporalHierarchy):
    """Faculty Enrollment Model."""

    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
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

    def clean(self):
        super().clean()
        if not self.facility_enrollment or not self.quarters:
            raise ValidationError("Faculty enrollments require quarters assignment.")
        capacity = self.quarters.capacity or 0
        if capacity > 0:
            qs = FacultyEnrollment.objects.filter(
                facility_enrollment=self.facility_enrollment,
                quarters=self.quarters,
            ).exclude(pk=self.pk)
            if qs.count() >= capacity:
                raise ValidationError("Selected quarters are already full for faculty.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = (
                FacultyEnrollment.objects.select_related(
                    "facility_enrollment", "quarters"
                )
                .only("facility_enrollment", "quarters")
                .get(pk=self.pk)
            )
        if self.facility_enrollment and not self.start:
            self.start = self.facility_enrollment.start
        if self.facility_enrollment and not self.end:
            self.end = self.facility_enrollment.end
        result = super().save(*args, **kwargs)
        self._sync_quarters_reservation(previous)
        return result

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self._release_current_quarters()
        return super().delete(*args, **kwargs)

    def _availability_lookup(self, quarters=None):
        quarters = quarters or self.quarters
        if not self.facility_enrollment or not quarters:
            return None
        return {
            "facility_enrollment": self.facility_enrollment,
            "quarters": quarters,
        }

    def _sync_quarters_reservation(self, previous):
        changed = (
            previous
            and (
                previous.quarters_id != self.quarters_id
                or previous.facility_enrollment_id != self.facility_enrollment_id
            )
        )
        if changed:
            previous._release_current_quarters()
        self._reserve_current_quarters()

    def _reserve_current_quarters(self):
        lookup = self._availability_lookup()
        if not lookup:
            return
        availability, _ = FacultyQuartersAvailability.objects.get_or_create(
            defaults={"capacity": self.quarters.capacity or 1}, **lookup
        )
        availability.reserve_slot()

    def _release_current_quarters(self):
        lookup = self._availability_lookup()
        if not lookup:
            return
        try:
            availability = FacultyQuartersAvailability.objects.get(**lookup)
        except FacultyQuartersAvailability.DoesNotExist:
            return
        availability.release_slot()
