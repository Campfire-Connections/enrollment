""" Enrollment Related QuerySets."""

from pages.querysets import AbstractBaseQuerySet
from django.db import models


class LeaderEnrollmentQuerySet(AbstractBaseQuerySet):
    def by_faction_enrollment(self, faction_enrollment_id):
        return self.filter(faction_enrollment_id=faction_enrollment_id)


class AttendeeEnrollmentQuerySet(AbstractBaseQuerySet):
    def by_faction_enrollment(self, faction_enrollment_id):
        return self.filter(faction_enrollment_id=faction_enrollment_id)

    def with_related(self):
        return self.select_related(
            "attendee__user",
            "attendee__faction",
            "faction_enrollment__faction",
            "faction_enrollment__week",
            "quarters",
        )


class FactionEnrollmentQuerySet(AbstractBaseQuerySet):
    def active(self):
        """
        Returns factions that are currently active.
        """
        return self.filter(is_active=True)

    def by_faction(self, faction_id):
        """
        Returns enrollments belonging to a specific faction.
        """
        return self.filter(faction_id=faction_id)

    def with_related(self):
        return self.select_related(
            "facility_enrollment",
            "facility_enrollment__facility",
            "facility_enrollment__organization_enrollment",
            "faction",
            "week",
            "quarters",
        )


class FacilityEnrollmentQuerySet(AbstractBaseQuerySet):
    def with_schedule(self):
        return (
            self.select_related("facility", "organization_enrollment")
            .prefetch_related(
                "weeks",
                "weeks__periods",
                "faction_enrollments__faction",
                "faction_enrollments__quarters",
            )
        )


class FacultyEnrollmentQuerySet(AbstractBaseQuerySet):
    def classes_for_faculty(self, faculty_profile, facility_enrollment=None):
        """
        Fetch the classes for a given faculty and facility enrollment.
        """
        qs = self.filter(faculty=faculty_profile)

        if facility_enrollment:
            qs = qs.filter(facility_enrollment=facility_enrollment)

        # Traverse relationships to access FacilityClass
        return qs.values(
            "facility_enrollment__facility_classes__name",
            "facility_enrollment__facility_classes__id",
        )
