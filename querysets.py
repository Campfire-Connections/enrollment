""" Enrollment Related QuerySets."""

from pages.querysets import AbstractBaseQuerySet

class LeaderEnrollmentQuerySet(AbstractBaseQuerySet):
    def by_faction_enrollment(self, faction_enrollment_id):
        return self.filter(faction_enrollment_id=faction_enrollment_id)


class AttendeeEnrollmentQuerySet(AbstractBaseQuerySet):
    def by_faction_enrollment(self, faction_enrollment_id):
        return self.filter(faction_enrollment_id=faction_enrollment_id)


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

from django.db import models

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
