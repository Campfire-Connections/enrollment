from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models


class BaseAvailability(models.Model):
    capacity = models.PositiveIntegerField()
    reserved = models.PositiveIntegerField(default=0)
    on_hold = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def remaining(self):
        return max(self.capacity - self.reserved - self.on_hold, 0)

    def reserve(self, amount=1):
        if amount <= 0:
            return
        if self.reserved + amount > self.capacity:
            raise ValidationError("Capacity exceeded for this resource.")
        self.reserved += amount
        self.save(update_fields=["reserved", "updated_at"])

    def release(self, amount=1):
        if amount <= 0:
            return
        self.reserved = max(self.reserved - amount, 0)
        self.save(update_fields=["reserved", "updated_at"])

    def cache_key(self):
        return f"availability:{self.__class__.__name__}:{self.pk}"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        cache.delete(self.cache_key())
        return result


class QuartersWeekAvailability(BaseAvailability):
    facility_enrollment = models.ForeignKey(
        "enrollment.FacilityEnrollment",
        on_delete=models.CASCADE,
        related_name="quarters_availability",
    )
    week = models.ForeignKey(
        "enrollment.Week",
        on_delete=models.CASCADE,
        related_name="quarters_availability",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="week_availability",
    )

    class Meta:
        unique_together = ("week", "quarters")
        indexes = [models.Index(fields=["facility_enrollment", "week"])]

    @property
    def is_reserved(self):
        return self.reserved >= self.capacity

    def reserve_full(self):
        if self.is_reserved:
            raise ValidationError(
                "These quarters are already reserved for the selected week."
            )
        self.reserved = self.capacity
        self.save(update_fields=["reserved", "updated_at"])

    def release_full(self):
        if self.reserved == 0:
            return
        self.reserved = 0
        self.save(update_fields=["reserved", "updated_at"])


class FacilityClassAvailability(BaseAvailability):
    facility_class_enrollment = models.OneToOneField(
        "enrollment.FacilityClassEnrollment",
        on_delete=models.CASCADE,
        related_name="availability",
    )

    class Meta:
        indexes = [models.Index(fields=["facility_class_enrollment"])]

    def ensure_capacity(self, capacity):
        if capacity <= 0:
            raise ValidationError("Capacity must be greater than zero.")
        if self.capacity != capacity:
            self.capacity = capacity
            if self.reserved > self.capacity:
                self.reserved = self.capacity
            self.save(update_fields=["capacity", "reserved", "updated_at"])

    @classmethod
    def for_enrollment(cls, enrollment):
        availability, _ = cls.objects.get_or_create(
            facility_class_enrollment=enrollment,
            defaults={"capacity": enrollment.max_enrollment},
        )
        availability.ensure_capacity(enrollment.max_enrollment)
        return availability


class FacultyQuartersAvailability(BaseAvailability):
    facility_enrollment = models.ForeignKey(
        "enrollment.FacilityEnrollment",
        on_delete=models.CASCADE,
        related_name="faculty_quarters_availability",
    )
    quarters = models.ForeignKey(
        "facility.Quarters",
        on_delete=models.CASCADE,
        related_name="faculty_availability",
    )

    class Meta:
        unique_together = ("facility_enrollment", "quarters")
        indexes = [models.Index(fields=["facility_enrollment", "quarters"])]

    def reserve_slot(self):
        if self.remaining <= 0:
            raise ValidationError("Faculty quarters are already at capacity.")
        self.reserve()

    def release_slot(self):
        self.release()
