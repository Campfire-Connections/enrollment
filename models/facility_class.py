# enrollment/models/facility_class.py

from django.db import models

from core.mixins import models as mixins
from core.mixins import settings as stgs

from .organization import OrganizationEnrollment
from .temporal import Period
from .availability import FacilityClassAvailability


class FacilityClassEnrollment(
    mixins.NameDescriptionMixin,
    mixins.TimestampMixin,
    mixins.SoftDeleteMixin,
    mixins.AuditMixin,
    mixins.SlugMixin,
    mixins.ActiveMixin,
    models.Model,
):
    """Facility Class Enrollment Model."""

    facility_class = models.ForeignKey("course.FacilityClass", on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    department = models.ForeignKey("facility.Department", on_delete=models.CASCADE)
    organization_enrollment = models.ForeignKey(
        OrganizationEnrollment, on_delete=models.CASCADE
    )
    max_enrollment = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "Facility Class Enrollment"
        verbose_name_plural = "Facility Class Enrollments"
        ordering = ["facility_class__name", "period__start"]
        indexes = [models.Index(fields=["facility_class", "period"])]

    def __str__(self):
        return f"{self.facility_class} - {self.period} - {self.department}"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        FacilityClassAvailability.for_enrollment(self)
        return result
