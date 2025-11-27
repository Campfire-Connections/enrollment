from django.contrib import admin

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.faculty import FacultyEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty_class import FacultyClassEnrollment


class TimestampedEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(
    AttendeeEnrollment,
    LeaderEnrollment,
    FactionEnrollment,
    FacultyEnrollment,
    FacilityClassEnrollment,
)
class EnrollmentAuditAdmin(TimestampedEnrollmentAdmin):
    pass


@admin.register(FacultyClassEnrollment)
class FacultyClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__")
