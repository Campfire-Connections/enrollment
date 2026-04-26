from dataclasses import dataclass

from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.availability import (
    FacilityClassAvailability,
    FacultyQuartersAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.faction import FactionEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty import FacultyEnrollment


@dataclass
class AvailabilityIssue:
    kind: str
    label: str
    severity: str
    expected: str
    actual: str


def build_availability_status():
    issues = []
    holds = []
    full = []

    _collect_faction_quarters(issues, holds, full)
    _collect_faculty_quarters(issues, holds, full)
    _collect_class_availability(issues, holds, full)

    return {
        "issues": issues,
        "holds": holds,
        "full": full,
        "summary": {
            "issues": len(issues),
            "holds": len(holds),
            "full": len(full),
        },
    }


def _collect_faction_quarters(issues, holds, full):
    expected = {
        (
            enrollment.facility_enrollment_id,
            enrollment.week_id,
            enrollment.quarters_id,
        ): enrollment
        for enrollment in FactionEnrollment.objects.select_related(
            "facility_enrollment__facility", "week", "quarters", "faction"
        )
    }
    for key, enrollment in expected.items():
        label = (
            f"{enrollment.faction} / {enrollment.week} / {enrollment.quarters}"
        )
        try:
            availability = QuartersWeekAvailability.objects.get(
                facility_enrollment_id=key[0],
                week_id=key[1],
                quarters_id=key[2],
            )
        except QuartersWeekAvailability.DoesNotExist:
            issues.append(
                AvailabilityIssue(
                    "faction_quarters",
                    label,
                    "critical",
                    f"reserved={enrollment.quarters.capacity}",
                    "missing availability row",
                )
            )
            continue
        _track_common(
            issues,
            holds,
            full,
            "faction_quarters",
            label,
            availability,
            expected_reserved=enrollment.quarters.capacity,
            expected_capacity=enrollment.quarters.capacity,
        )

    for availability in QuartersWeekAvailability.objects.exclude(reserved=0):
        key = (
            availability.facility_enrollment_id,
            availability.week_id,
            availability.quarters_id,
        )
        if key not in expected:
            issues.append(
                AvailabilityIssue(
                    "faction_quarters",
                    str(availability.quarters),
                    "warning",
                    "reserved=0",
                    f"reserved={availability.reserved}",
                )
            )


def _collect_faculty_quarters(issues, holds, full):
    expected = {}
    labels = {}
    for enrollment in FacultyEnrollment.objects.select_related(
        "facility_enrollment__facility", "quarters", "faculty__user"
    ):
        key = (enrollment.facility_enrollment_id, enrollment.quarters_id)
        expected.setdefault(
            key,
            {"reserved": 0, "capacity": enrollment.quarters.capacity or 1},
        )
        expected[key]["reserved"] += 1
        labels[key] = f"{enrollment.facility_enrollment.facility} / {enrollment.quarters}"

    for key, values in expected.items():
        try:
            availability = FacultyQuartersAvailability.objects.get(
                facility_enrollment_id=key[0],
                quarters_id=key[1],
            )
        except FacultyQuartersAvailability.DoesNotExist:
            issues.append(
                AvailabilityIssue(
                    "faculty_quarters",
                    labels[key],
                    "critical",
                    str(values),
                    "missing availability row",
                )
            )
            continue
        _track_common(
            issues,
            holds,
            full,
            "faculty_quarters",
            labels[key],
            availability,
            expected_reserved=values["reserved"],
            expected_capacity=values["capacity"],
        )

    for availability in FacultyQuartersAvailability.objects.exclude(reserved=0):
        key = (availability.facility_enrollment_id, availability.quarters_id)
        if key not in expected:
            issues.append(
                AvailabilityIssue(
                    "faculty_quarters",
                    str(availability.quarters),
                    "warning",
                    "reserved=0",
                    f"reserved={availability.reserved}",
                )
            )


def _collect_class_availability(issues, holds, full):
    schedules = FacilityClassEnrollment.objects.select_related(
        "facility_class", "period", "department"
    )
    for schedule in schedules:
        label = str(schedule)
        expected_reserved = AttendeeClassEnrollment.objects.filter(
            facility_class_enrollment=schedule
        ).count()
        try:
            availability = FacilityClassAvailability.objects.get(
                facility_class_enrollment=schedule
            )
        except FacilityClassAvailability.DoesNotExist:
            issues.append(
                AvailabilityIssue(
                    "class",
                    label,
                    "critical",
                    f"reserved={expected_reserved}, capacity={schedule.max_enrollment}",
                    "missing availability row",
                )
            )
            continue
        _track_common(
            issues,
            holds,
            full,
            "class",
            label,
            availability,
            expected_reserved=expected_reserved,
            expected_capacity=schedule.max_enrollment,
        )


def _track_common(
    issues,
    holds,
    full,
    kind,
    label,
    availability,
    *,
    expected_reserved,
    expected_capacity,
):
    if availability.reserved != expected_reserved or availability.capacity != expected_capacity:
        issues.append(
            AvailabilityIssue(
                kind,
                label,
                "warning",
                f"reserved={expected_reserved}, capacity={expected_capacity}",
                f"reserved={availability.reserved}, capacity={availability.capacity}",
            )
        )
    if availability.on_hold:
        holds.append({"kind": kind, "label": label, "availability": availability})
    if availability.remaining <= 0:
        full.append({"kind": kind, "label": label, "availability": availability})
