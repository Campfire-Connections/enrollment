from django.contrib import admin

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.faculty import FacultyEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty_class import FacultyClassEnrollment
from enrollment.services import SchedulingService


class TimestampedEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(
    AttendeeEnrollment,
    LeaderEnrollment,
    FacilityClassEnrollment,
)
class EnrollmentAuditAdmin(TimestampedEnrollmentAdmin):
    pass


class SchedulingServiceAdminMixin:
    service_drop_method = None

    def get_service(self, request):
        return SchedulingService(user=getattr(request, "user", None))

    def delete_model(self, request, obj):
        drop_method = self.service_drop_method
        if not drop_method:
            return super().delete_model(request, obj)
        method = getattr(self.get_service(request), drop_method)
        method(**{self.service_object_kwarg: obj})

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)


@admin.register(FactionEnrollment)
class FactionEnrollmentAdmin(SchedulingServiceAdminMixin, TimestampedEnrollmentAdmin):
    service_drop_method = "drop_faction_enrollment"
    service_object_kwarg = "faction_enrollment"

    def save_model(self, request, obj, form, change):
        instance = FactionEnrollment.objects.get(pk=obj.pk) if change else None
        self.get_service(request).schedule_faction_enrollment(
            faction=obj.faction,
            facility_enrollment=obj.facility_enrollment,
            week=obj.week,
            quarters=obj.quarters,
            start=obj.start,
            end=obj.end,
            name=obj.name,
            description=obj.description,
            faction_enrollment=instance,
        )


@admin.register(FacultyEnrollment)
class FacultyEnrollmentAdmin(SchedulingServiceAdminMixin, TimestampedEnrollmentAdmin):
    service_drop_method = "drop_faculty_enrollment"
    service_object_kwarg = "faculty_enrollment"

    def save_model(self, request, obj, form, change):
        instance = FacultyEnrollment.objects.get(pk=obj.pk) if change else None
        self.get_service(request).schedule_faculty_enrollment(
            faculty=obj.faculty,
            facility_enrollment=obj.facility_enrollment,
            quarters=obj.quarters,
            role=obj.role,
            instance=instance,
        )


@admin.register(AttendeeClassEnrollment)
class AttendeeClassEnrollmentAdmin(SchedulingServiceAdminMixin, admin.ModelAdmin):
    list_display = ("id", "__str__")
    service_drop_method = "drop_attendee_from_class"
    service_object_kwarg = "attendee_class_enrollment"

    def save_model(self, request, obj, form, change):
        instance = AttendeeClassEnrollment.objects.get(pk=obj.pk) if change else None
        self.get_service(request).assign_attendee_to_class(
            attendee=obj.attendee,
            attendee_enrollment=obj.attendee_enrollment,
            facility_class_enrollment=obj.facility_class_enrollment,
            attendee_class_enrollment=instance,
        )


@admin.register(FacultyClassEnrollment)
class FacultyClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
