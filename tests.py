from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from core.tests import BaseDomainTestCase, mute_profile_signals
from enrollment.models.availability import (
    FacilityClassAvailability,
    QuartersWeekAvailability,
)
from enrollment.models.attendee_class import AttendeeClassEnrollment
from enrollment.models.faction import FactionEnrollment
from enrollment.models.facility import FacilityEnrollment
from enrollment.models.facility_class import FacilityClassEnrollment
from enrollment.models.temporal import Period, Week
from facility.models.department import Department
from facility.models.quarters import Quarters, QuartersType
from faction.models.attendee import AttendeeProfile
from course.models.facility_class import FacilityClass

User = get_user_model()


class OrganizationEnrollmentTests(BaseDomainTestCase):
    def test_get_courses_returns_related_instances(self):
        courses = self.org_enrollment.get_courses()
        self.assertIn(self.org_course, courses)


class AvailabilityTrackingTests(BaseDomainTestCase):
    def setUp(self):
        self.week = Week.objects.create(
            name="Week 1",
            start=self.facility_enrollment.start,
            end=self.facility_enrollment.start + timedelta(days=6),
            facility_enrollment=self.facility_enrollment,
        )
        self.quarters_type = QuartersType.objects.create(
            name="Cabin", organization=self.organization
        )
        self.quarters = Quarters.objects.create(
            name="Cabin 1",
            capacity=12,
            type=self.quarters_type,
            facility=self.facility,
        )

    def test_faction_enrollment_reserves_quarters(self):
        FactionEnrollment.objects.create(
            facility_enrollment=self.facility_enrollment,
            start=self.week.start,
            end=self.week.end,
            faction=self.faction,
            week=self.week,
            quarters=self.quarters,
            name="Eagle Week One",
        )
        availability = QuartersWeekAvailability.objects.get(
            week=self.week, quarters=self.quarters
        )
        self.assertTrue(availability.is_reserved)
        self.assertEqual(availability.capacity, self.quarters.capacity)

        with self.assertRaises(ValidationError):
            FactionEnrollment.objects.create(
                facility_enrollment=self.facility_enrollment,
                start=self.week.start,
                end=self.week.end,
                faction=self.faction,
                week=self.week,
                quarters=self.quarters,
                name="Eagle Week One Retry",
            )

    def test_class_enrollment_updates_availability(self):
        department = Department.objects.create(
            name="Program",
            abbreviation="PRG",
            facility=self.facility,
        )
        period = Period.objects.create(
            name="Morning",
            start=time(8, 0),
            end=time(9, 0),
            week=self.week,
        )
        facility_class = FacilityClass.objects.create(
            name="First Aid",
            organization_course=self.org_course,
            facility_enrollment=self.facility_enrollment,
            max_enrollment=10,
        )
        facility_class_enrollment = FacilityClassEnrollment.objects.create(
            facility_class=facility_class,
            period=period,
            department=department,
            organization_enrollment=self.org_enrollment,
            max_enrollment=10,
        )
        availability = FacilityClassAvailability.for_enrollment(
            facility_class_enrollment
        )
        self.assertEqual(availability.capacity, 10)

        with mute_profile_signals():
            user = User.objects.create_user(
                username="attendee.availability",
                password="pass12345",
                user_type=User.UserType.ATTENDEE,
            )
        attendee = AttendeeProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )
        enrollment = AttendeeClassEnrollment.objects.create(
            attendee=attendee,
            facility_class_enrollment=facility_class_enrollment,
        )
        availability.refresh_from_db()
        self.assertEqual(availability.reserved, 1)

        enrollment.delete()
        availability.refresh_from_db()
        self.assertEqual(availability.reserved, 0)

    def test_facility_enrollment_queryset_prefetches_schedule(self):
        enrollment = FacilityEnrollment.objects.with_schedule().get(
            pk=self.facility_enrollment.pk
        )
        with self.assertNumQueries(0):
            list(enrollment.weeks.all())

    def test_faction_enrollment_queryset_selects_related(self):
        faction_enrollment = FactionEnrollment.objects.create(
            facility_enrollment=self.facility_enrollment,
            start=self.week.start,
            end=self.week.end,
            faction=self.faction,
            week=self.week,
            quarters=self.quarters,
            name="Eagle Week One",
        )
        enrollment = FactionEnrollment.objects.with_related().get(
            pk=faction_enrollment.pk
        )
        with self.assertNumQueries(0):
            _ = enrollment.facility_enrollment.facility.name
            _ = enrollment.week.name
            _ = enrollment.quarters.name
