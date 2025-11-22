from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

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
from facility.models.faculty import FacultyProfile
from faction.models.attendee import AttendeeProfile
from faction.models.leader import LeaderProfile
from enrollment.models.faculty import FacultyEnrollment
from course.models.facility_class import FacilityClass
from enrollment.serializers import (
    AttendeeEnrollmentSerializer,
    LeaderEnrollmentSerializer,
)
from enrollment.services import SchedulingService
from enrollment.views.leader import LeaderEnrollmenyViewSet

User = get_user_model()


class OrganizationEnrollmentTests(BaseDomainTestCase):
    def test_get_courses_returns_related_instances(self):
        courses = self.org_enrollment.get_courses()
        self.assertIn(self.org_course, courses)


class EnrollmentScenarioBase(BaseDomainTestCase):
    def setUp(self):
        super().setUp()
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

    def _build_facility_class_enrollment(self, max_enrollment=10):
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
            max_enrollment=max_enrollment,
        )
        return FacilityClassEnrollment.objects.create(
            facility_class=facility_class,
            period=period,
            department=department,
            organization_enrollment=self.org_enrollment,
            max_enrollment=max_enrollment,
        )

    def _create_attendee_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.ATTENDEE,
            )
        return AttendeeProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )

    def _create_faction_enrollment(self, name, quarters=None, week=None):
        week = week or self.week
        quarters = quarters or self.quarters
        return FactionEnrollment.objects.create(
            facility_enrollment=self.facility_enrollment,
            start=week.start,
            end=week.end,
            faction=self.faction,
            week=week,
            quarters=quarters,
            name=name,
        )

    def _create_faculty_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.FACULTY,
            )
        return FacultyProfile.objects.create(
            user=user,
            organization=self.organization,
            facility=self.facility,
        )

    def _create_leader_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        return LeaderProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )

class AvailabilityTrackingTests(EnrollmentScenarioBase):
    def test_faction_enrollment_reserves_quarters(self):
        self._create_faction_enrollment(name="Eagle Week One")
        availability = QuartersWeekAvailability.objects.get(
            week=self.week, quarters=self.quarters
        )
        self.assertTrue(availability.is_reserved)
        self.assertEqual(availability.capacity, self.quarters.capacity)

        with self.assertRaises(ValidationError):
            self._create_faction_enrollment(name="Eagle Week One Retry")

    def test_class_enrollment_updates_availability(self):
        facility_class_enrollment = self._build_facility_class_enrollment()
        availability = FacilityClassAvailability.for_enrollment(
            facility_class_enrollment
        )
        self.assertEqual(availability.capacity, 10)

        attendee = self._create_attendee_profile("attendee.availability")
        enrollment = AttendeeClassEnrollment.objects.create(
            attendee=attendee,
            facility_class_enrollment=facility_class_enrollment,
        )
        availability.refresh_from_db()
        self.assertEqual(availability.reserved, 1)

        enrollment.delete()
        availability.refresh_from_db()
        self.assertEqual(availability.reserved, 0)

    def test_scheduling_service_prevents_overbooking(self):
        facility_class_enrollment = self._build_facility_class_enrollment(
            max_enrollment=1
        )
        attendee_one = self._create_attendee_profile("attendee.service.one")
        attendee_two = self._create_attendee_profile("attendee.service.two")
        service = SchedulingService()
        service.assign_attendee_to_class(
            attendee=attendee_one,
            facility_class_enrollment=facility_class_enrollment,
        )
        with self.assertRaises(ValidationError):
            service.assign_attendee_to_class(
                attendee=attendee_two,
                facility_class_enrollment=facility_class_enrollment,
            )

    def test_facility_enrollment_queryset_prefetches_schedule(self):
        enrollment = FacilityEnrollment.objects.with_schedule().get(
            pk=self.facility_enrollment.pk
        )
        with self.assertNumQueries(0):
            list(enrollment.weeks.all())

    def test_faction_enrollment_queryset_selects_related(self):
        faction_enrollment = self._create_faction_enrollment(
            name="Eagle Week One Again"
        )
        enrollment = FactionEnrollment.objects.with_related().get(
            pk=faction_enrollment.pk
        )
        with self.assertNumQueries(0):
            _ = enrollment.facility_enrollment.facility.name
            _ = enrollment.week.name
            _ = enrollment.quarters.name

    def test_attendee_enrollment_service_enforces_capacity(self):
        limited_quarters = Quarters.objects.create(
            name="Limited Hut",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faction_enrollment = self._create_faction_enrollment(
            name="Limited Week",
            quarters=limited_quarters,
        )
        attendee_one = self._create_attendee_profile("attendee.service.one")
        attendee_two = self._create_attendee_profile("attendee.service.two")
        service = SchedulingService()
        service.schedule_attendee_enrollment(
            attendee=attendee_one,
            faction_enrollment=faction_enrollment,
        )
        with self.assertRaises(ValidationError):
            service.schedule_attendee_enrollment(
                attendee=attendee_two,
                faction_enrollment=faction_enrollment,
            )

    def test_faculty_enrollment_service_enforces_capacity(self):
        staff_quarters = Quarters.objects.create(
            name="Staff Cabin",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faculty_one = self._create_faculty_profile("faculty.service.one")
        faculty_two = self._create_faculty_profile("faculty.service.two")
        service = SchedulingService()
        service.schedule_faculty_enrollment(
            faculty=faculty_one,
            facility_enrollment=self.facility_enrollment,
            quarters=staff_quarters,
        )
        with self.assertRaises(ValidationError):
            service.schedule_faculty_enrollment(
                faculty=faculty_two,
                facility_enrollment=self.facility_enrollment,
                quarters=staff_quarters,
            )

    def test_leader_enrollment_service_enforces_capacity(self):
        limited_quarters = Quarters.objects.create(
            name="Leader Cabin",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faction_enrollment = self._create_faction_enrollment(
            name="Leader Week",
            quarters=limited_quarters,
        )
        leader_one = self._create_leader_profile("leader.service.one")
        leader_two = self._create_leader_profile("leader.service.two")
        service = SchedulingService()
        service.schedule_leader_enrollment(
            leader=leader_one,
            faction_enrollment=faction_enrollment,
            quarters=limited_quarters,
        )
        with self.assertRaises(ValidationError):
            service.schedule_leader_enrollment(
                leader=leader_two,
                faction_enrollment=faction_enrollment,
                quarters=limited_quarters,
            )


class SchedulingServiceUpdateTests(EnrollmentScenarioBase):
    def test_attendee_enrollment_update_does_not_block_self(self):
        tight_quarters = Quarters.objects.create(
            name="Cabin Tight",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faction_enrollment = self._create_faction_enrollment(
            name="Tight Week",
            quarters=tight_quarters,
        )
        attendee = self._create_attendee_profile("attendee.single")
        service = SchedulingService()
        enrollment = service.schedule_attendee_enrollment(
            attendee=attendee,
            faction_enrollment=faction_enrollment,
            quarters=tight_quarters,
        )
        updated = service.schedule_attendee_enrollment(
            attendee=attendee,
            faction_enrollment=faction_enrollment,
            quarters=tight_quarters,
            role="assistant",
            attendee_enrollment=enrollment,
        )
        self.assertEqual(enrollment.pk, updated.pk)
        self.assertEqual(updated.role, "assistant")

    def test_attendee_class_enrollment_update_respects_capacity(self):
        facility_class_enrollment = self._build_facility_class_enrollment(
            max_enrollment=1
        )
        attendee = self._create_attendee_profile("attendee.class.one")
        service = SchedulingService()
        enrollment = service.assign_attendee_to_class(
            attendee=attendee,
            facility_class_enrollment=facility_class_enrollment,
        )
        updated = service.assign_attendee_to_class(
            attendee=attendee,
            facility_class_enrollment=facility_class_enrollment,
            attendee_class_enrollment=enrollment,
        )
        self.assertEqual(enrollment.pk, updated.pk)

        other_attendee = self._create_attendee_profile("attendee.class.two")
        with self.assertRaises(ValidationError):
            service.assign_attendee_to_class(
                attendee=other_attendee,
                facility_class_enrollment=facility_class_enrollment,
            )


class SerializerSchedulingTests(EnrollmentScenarioBase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    def test_leader_serializer_creates_enrollment(self):
        leader = self._create_leader_profile("leader.serializer.one")
        faction_enrollment = self._create_faction_enrollment("Serializer Week")
        serializer = LeaderEnrollmentSerializer(
            data={
                "leader": leader.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": self.quarters.pk,
                "role": "Mentor",
            },
            context={"request": self.factory.post("/")},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.leader, leader)

    def test_leader_serializer_handles_capacity_error(self):
        limited = Quarters.objects.create(
            name="Limited Leader Hut",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faction_enrollment = self._create_faction_enrollment(
            "Serializer Limited", quarters=limited
        )
        leader_one = self._create_leader_profile("leader.serializer.A")
        leader_two = self._create_leader_profile("leader.serializer.B")

        serializer = LeaderEnrollmentSerializer(
            data={
                "leader": leader_one.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": limited.pk,
            },
            context={"request": self.factory.post("/")},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()

        serializer_two = LeaderEnrollmentSerializer(
            data={
                "leader": leader_two.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": limited.pk,
            },
            context={"request": self.factory.post("/")},
        )
        self.assertTrue(serializer_two.is_valid(), serializer_two.errors)
        with self.assertRaises(DRFValidationError):
            serializer_two.save()

    def test_attendee_serializer_creates_enrollment(self):
        attendee = self._create_attendee_profile("attendee.serializer.one")
        faction_enrollment = self._create_faction_enrollment("Attendee Week")
        serializer = AttendeeEnrollmentSerializer(
            data={
                "attendee": attendee.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": self.quarters.pk,
            },
            context={"request": self.factory.post("/")},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.attendee, attendee)


class LeaderEnrollmentViewSetTests(EnrollmentScenarioBase):
    def setUp(self):
        super().setUp()
        self.factory = APIRequestFactory()

    def test_viewset_create(self):
        leader = self._create_leader_profile("leader.api.one")
        faction_enrollment = self._create_faction_enrollment("API Week")
        request = self.factory.post(
            "/api/",
            {
                "leader": leader.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": self.quarters.pk,
            },
            format="json",
        )
        force_authenticate(request, user=leader.user)
        response = LeaderEnrollmenyViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewset_capacity_error(self):
        limited = Quarters.objects.create(
            name="API Cabin",
            capacity=1,
            type=self.quarters_type,
            facility=self.facility,
        )
        faction_enrollment = self._create_faction_enrollment(
            "API Limited", quarters=limited
        )
        leader_one = self._create_leader_profile("leader.api.A")
        leader_two = self._create_leader_profile("leader.api.B")

        first_request = self.factory.post(
            "/api/",
            {
                "leader": leader_one.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": limited.pk,
            },
            format="json",
        )
        force_authenticate(first_request, user=leader_one.user)
        LeaderEnrollmenyViewSet.as_view({"post": "create"})(first_request)

        second_request = self.factory.post(
            "/api/",
            {
                "leader": leader_two.pk,
                "faction_enrollment": faction_enrollment.pk,
                "quarters": limited.pk,
            },
            format="json",
        )
        force_authenticate(second_request, user=leader_two.user)
        response = LeaderEnrollmenyViewSet.as_view({"post": "create"})(second_request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _build_facility_class_enrollment(self, max_enrollment=10):
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
            max_enrollment=max_enrollment,
        )
        return FacilityClassEnrollment.objects.create(
            facility_class=facility_class,
            period=period,
            department=department,
            organization_enrollment=self.org_enrollment,
            max_enrollment=max_enrollment,
        )

    def _create_attendee_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.ATTENDEE,
            )
        return AttendeeProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )

    def _create_faction_enrollment(self, name, quarters=None, week=None):
        week = week or self.week
        quarters = quarters or self.quarters
        return FactionEnrollment.objects.create(
            facility_enrollment=self.facility_enrollment,
            start=week.start,
            end=week.end,
            faction=self.faction,
            week=week,
            quarters=quarters,
            name=name,
        )

    def _create_faculty_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.FACULTY,
            )
        return FacultyProfile.objects.create(
            user=user,
            organization=self.organization,
            facility=self.facility,
        )

    def _create_leader_profile(self, username):
        with mute_profile_signals():
            user = User.objects.create_user(
                username=username,
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        return LeaderProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )
