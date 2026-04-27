from django.shortcuts import get_object_or_404

from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.facility import FacilityEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.temporal import Period, Week
from enrollment.tables.faction import FactionEnrollmentTable
from enrollment.tables.period import PeriodsByWeekTable, PeriodTable
from enrollment.tables.week import WeekTable
from faction.models.attendee import AttendeeProfile
from facility.models.faculty import FacultyProfile
from facility.models.quarters import Quarters, QuartersType
from facility.tables.faculty import FacultyTable


def weeks_for_facility_enrollment(facility_enrollment):
    return Week.objects.filter(facility_enrollment=facility_enrollment)


def weeks_for_facility_enrollment_id(facility_enrollment_id):
    return Week.objects.filter(facility_enrollment_id=facility_enrollment_id)


def periods_for_week(week):
    return Period.objects.filter(week=week)


def period_index_queryset():
    return Period.objects.select_related("week", "week__facility_enrollment").order_by(
        "week__start", "start", "name"
    )


def faction_enrollments_for_week(week):
    return FactionEnrollment.objects.filter(week=week)


def available_faction_quarters_for_week(*, week_id, facility_enrollment):
    faction_quarters_type = QuartersType.objects.get(slug="faction")
    used_quarters = FactionEnrollment.objects.filter(
        week_id=week_id,
        week__facility_enrollment=facility_enrollment,
    ).values_list("quarters_id", flat=True)
    return Quarters.objects.filter(
        facility=facility_enrollment.facility,
        type=faction_quarters_type,
    ).exclude(id__in=used_quarters)


def week_manage_tables_config(week):
    return {
        "periods": {
            "class": PeriodsByWeekTable,
            "queryset": periods_for_week(week),
            "paginate_by": 5,
        },
        "faction_enrollments": {
            "class": FactionEnrollmentTable,
            "queryset": faction_enrollments_for_week(week),
            "paginate_by": 10,
        },
    }


def week_detail_tables_config(week):
    return {
        "periods_table": {
            "class": PeriodTable,
            "queryset": periods_for_week(week),
            "paginate_by": None,
        }
    }


def get_facility_enrollment_with_schedule(slug):
    return get_object_or_404(FacilityEnrollment.objects.with_schedule(), slug=slug)


def faculty_for_facility_enrollment(enrollment):
    return FacultyProfile.objects.filter(
        faculty_enrollments__facility_enrollment=enrollment,
    ).select_related("user")


def facility_enrollment_manage_tables_config(enrollment):
    return {
        "weeks": {
            "class": WeekTable,
            "queryset": weeks_for_facility_enrollment(enrollment),
            "paginate_by": 7,
        },
        "faculty": {
            "class": FacultyTable,
            "queryset": faculty_for_facility_enrollment(enrollment),
        },
    }


def facility_enrollment_detail_tables_config(enrollment):
    return {
        "weeks_table": {
            "class": WeekTable,
            "queryset": weeks_for_facility_enrollment(enrollment),
        },
    }


def facility_enrollment_index_queryset(facility=None):
    qs = FacilityEnrollment.objects.with_schedule()
    if facility:
        qs = qs.filter(facility=facility)
    return qs


def leader_enrollment_queryset(leader_slug=None):
    qs = LeaderEnrollment.objects.with_related()
    if leader_slug:
        qs = qs.filter(leader__slug=leader_slug)
    return qs


def attendee_enrollments_for_attendee_slug(attendee_slug):
    return AttendeeEnrollment.objects.with_related().filter(attendee__slug=attendee_slug)


def get_attendee_by_slug(attendee_slug):
    return get_object_or_404(AttendeeProfile.objects.select_related("user"), slug=attendee_slug)
