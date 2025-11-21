# Enrollment App

`enrollment` coordinates every scheduling surface in Campfire Connections. It owns the models,
querysets, availability tracking, and service layer used by the faculty, leader, and attendee
portals.

## Responsibilities

- Temporal models for organization/facility/faction enrollments, weekly schedules, and periods.
- Availability tracking (`models/availability.py`) for quarters/cabins and facility classes.
- Scheduling service (`services/scheduling.py`) that enforces capacity rules and persists
  enrollments atomically regardless of which portal initiates the change.
- Forms, tables, serializers, and DRF viewsets for managing attendee, leader, faculty, and
  class enrollments.
- Context data for dashboards (`core/dashboard_data.py` pulls from these models).

## Key Features

- **Quarters & Class Availability** – `QuartersWeekAvailability`, `FacilityClassAvailability`,
  and `FacultyQuartersAvailability` keep remaining counts up-to-date.
- **SchedulingService** – single entry point for booking faction cabins, attendee cabins,
  leader cabins, faculty quarters, and class seats. All forms/serializers call into this
  service to ensure consistent validation.
- **Scoped Querysets** – `enrollment/querysets.py` provides `with_schedule()` and
  `with_related()` helpers to drastically cut query counts on dashboards.

## Usage Tips

- When adding a new enrollment flow, call the appropriate helper on `SchedulingService`
  instead of saving models directly. This automatically handles capacity errors and
  audit-side effects.
- Keep the seed data (`core/management/commands/seed_test_data.py`) in sync with any schema
  changes to these models so that developer refreshes continue to work.

## Tests

```bash
python manage.py test enrollment
```

The test suite covers availability tracking, scheduling service behavior, query optimizations,
and serializer integrity. Add regression cases here whenever you tweak the service or models.
