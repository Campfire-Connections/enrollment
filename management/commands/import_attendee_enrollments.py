import csv

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from enrollment.models.faction import FactionEnrollment
from enrollment.services import SchedulingService
from faction.models.attendee import AttendeeProfile
from facility.models.quarters import Quarters


class Command(BaseCommand):
    help = "Import attendee enrollments from CSV using scheduling service validation."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Persist rows. Without this flag the command only validates.",
        )

    def handle(self, *args, **options):
        path = options["csv_path"]
        commit = options["commit"]
        service = SchedulingService()
        created = 0
        errors = []

        try:
            csv_file = open(path, newline="")
        except OSError as exc:
            raise CommandError(f"Could not open CSV: {exc}") from exc

        with csv_file:
            reader = csv.DictReader(csv_file)
            required = {"attendee", "faction_enrollment", "quarters"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise CommandError(
                    "CSV is missing required column(s): " + ", ".join(sorted(missing))
                )

            with transaction.atomic():
                for line_number, row in enumerate(reader, start=2):
                    try:
                        attendee = self._get_attendee(row["attendee"])
                        faction_enrollment = FactionEnrollment.objects.get(
                            pk=row["faction_enrollment"]
                        )
                        quarters = Quarters.objects.get(pk=row["quarters"])
                        service.schedule_attendee_enrollment(
                            attendee=attendee,
                            faction_enrollment=faction_enrollment,
                            quarters=quarters,
                            role=row.get("role") or None,
                        )
                        created += 1
                    except (
                        AttendeeProfile.DoesNotExist,
                        FactionEnrollment.DoesNotExist,
                        Quarters.DoesNotExist,
                        ValidationError,
                    ) as exc:
                        errors.append(f"line {line_number}: {exc}")
                if errors or not commit:
                    transaction.set_rollback(True)

        if errors:
            self.stdout.write(self.style.ERROR(f"Import failed with {len(errors)} error(s):"))
            for error in errors:
                self.stdout.write(f"- {error}")
            raise CommandError("No rows were committed.")

        mode = "Imported" if commit else "Validated"
        self.stdout.write(self.style.SUCCESS(f"{mode} {created} attendee enrollment(s)."))

    def _get_attendee(self, value):
        if value.isdigit():
            return AttendeeProfile.objects.get(pk=value)
        return AttendeeProfile.objects.get(user__username=value)
