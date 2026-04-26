from django.core.management.base import BaseCommand
from django.db import transaction

from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.availability import (
    FacilityClassAvailability,
    FacultyQuartersAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.faction import FactionEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.faculty import FacultyEnrollment


class Command(BaseCommand):
    help = "Report and optionally repair scheduling availability counters."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Apply repairs instead of only reporting drift.",
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        issues = []
        with transaction.atomic():
            issues.extend(self._check_faction_quarters(fix))
            issues.extend(self._check_faculty_quarters(fix))
            issues.extend(self._check_class_availability(fix))

        if not issues:
            self.stdout.write(self.style.SUCCESS("Availability is reconciled."))
            return

        action = "Repaired" if fix else "Found"
        self.stdout.write(self.style.WARNING(f"{action} {len(issues)} issue(s):"))
        for issue in issues:
            self.stdout.write(f"- {issue}")

    def _check_faction_quarters(self, fix):
        issues = []
        expected = {
            (
                enrollment.facility_enrollment_id,
                enrollment.week_id,
                enrollment.quarters_id,
            ): enrollment.quarters.capacity
            for enrollment in FactionEnrollment.objects.select_related("quarters")
        }
        for key, expected_reserved in expected.items():
            facility_enrollment_id, week_id, quarters_id = key
            availability = self._get_or_create(
                QuartersWeekAvailability,
                fix,
                {
                    "facility_enrollment_id": facility_enrollment_id,
                    "week_id": week_id,
                    "quarters_id": quarters_id,
                },
                {"capacity": expected_reserved},
            )
            if availability is None:
                issues.append(f"Missing faction quarters availability {key}")
                continue
            if (
                availability.capacity != expected_reserved
                or availability.reserved != expected_reserved
            ):
                issues.append(
                    "Faction quarters availability drift "
                    f"{key}: reserved={availability.reserved}, "
                    f"capacity={availability.capacity}, expected={expected_reserved}"
                )
                if fix:
                    availability.capacity = expected_reserved
                    availability.reserved = expected_reserved
                    availability.save(update_fields=["capacity", "reserved", "updated_at"])

        for availability in QuartersWeekAvailability.objects.exclude(
            reserved=0
        ).select_related("quarters"):
            key = (
                availability.facility_enrollment_id,
                availability.week_id,
                availability.quarters_id,
            )
            if key not in expected:
                issues.append(f"Stale faction quarters reservation {key}")
                if fix:
                    availability.reserved = 0
                    availability.save(update_fields=["reserved", "updated_at"])
        return issues

    def _check_faculty_quarters(self, fix):
        issues = []
        expected = {}
        for enrollment in FacultyEnrollment.objects.select_related("quarters"):
            key = (enrollment.facility_enrollment_id, enrollment.quarters_id)
            capacity = enrollment.quarters.capacity or 1
            if key not in expected:
                expected[key] = {"reserved": 0, "capacity": capacity}
            expected[key]["reserved"] += 1
            expected[key]["capacity"] = capacity

        for key, values in expected.items():
            facility_enrollment_id, quarters_id = key
            availability = self._get_or_create(
                FacultyQuartersAvailability,
                fix,
                {
                    "facility_enrollment_id": facility_enrollment_id,
                    "quarters_id": quarters_id,
                },
                {"capacity": values["capacity"]},
            )
            if availability is None:
                issues.append(f"Missing faculty quarters availability {key}")
                continue
            if (
                availability.capacity != values["capacity"]
                or availability.reserved != values["reserved"]
            ):
                issues.append(
                    "Faculty quarters availability drift "
                    f"{key}: reserved={availability.reserved}, "
                    f"capacity={availability.capacity}, expected={values}"
                )
                if fix:
                    availability.capacity = values["capacity"]
                    availability.reserved = values["reserved"]
                    availability.save(update_fields=["capacity", "reserved", "updated_at"])

        for availability in FacultyQuartersAvailability.objects.exclude(reserved=0):
            key = (availability.facility_enrollment_id, availability.quarters_id)
            if key not in expected:
                issues.append(f"Stale faculty quarters reservation {key}")
                if fix:
                    availability.reserved = 0
                    availability.save(update_fields=["reserved", "updated_at"])
        return issues

    def _check_class_availability(self, fix):
        issues = []
        expected = {
            enrollment.pk: {
                "capacity": enrollment.max_enrollment,
                "reserved": AttendeeClassEnrollment.objects.filter(
                    facility_class_enrollment=enrollment
                ).count(),
            }
            for enrollment in FacilityClassEnrollment.objects.all()
        }
        for enrollment_id, values in expected.items():
            availability = self._get_or_create(
                FacilityClassAvailability,
                fix,
                {"facility_class_enrollment_id": enrollment_id},
                {"capacity": values["capacity"]},
            )
            if availability is None:
                issues.append(f"Missing class availability {enrollment_id}")
                continue
            if (
                availability.capacity != values["capacity"]
                or availability.reserved != values["reserved"]
            ):
                issues.append(
                    "Class availability drift "
                    f"{enrollment_id}: reserved={availability.reserved}, "
                    f"capacity={availability.capacity}, expected={values}"
                )
                if fix:
                    availability.capacity = values["capacity"]
                    availability.reserved = values["reserved"]
                    availability.save(update_fields=["capacity", "reserved", "updated_at"])
        return issues

    def _get_or_create(self, model, fix, lookup, defaults):
        try:
            return model.objects.get(**lookup)
        except model.DoesNotExist:
            if not fix:
                return None
            return model.objects.create(**lookup, **defaults)
