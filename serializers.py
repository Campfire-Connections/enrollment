"""
Enrollment serializers with service-backed creation for business rules.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from enrollment.models.faction import FactionEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.services import SchedulingService


class FactionEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactionEnrollment
        fields = [
            "id",
            "name",
            "description",
            "facility_enrollment",
            "start",
            "end",
            "faction",
            "week",
            "quarters",
            "slug",
        ]
        read_only_fields = ["id", "slug"]


class LeaderEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderEnrollment
        fields = [
            "id",
            "name",
            "description",
            "start",
            "end",
            "leader",
            "faction_enrollment",
            "quarters",
            "role",
            "slug",
        ]
        read_only_fields = ["id", "slug"]
        extra_kwargs = {
            "name": {"required": False},
            "start": {"required": False},
            "end": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        service = SchedulingService(user=getattr(request, "user", None))
        try:
            return service.schedule_leader_enrollment(**validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)


class AttendeeEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendeeEnrollment
        fields = [
            "id",
            "name",
            "description",
            "start",
            "end",
            "attendee",
            "faction_enrollment",
            "quarters",
            "role",
            "slug",
        ]
        read_only_fields = ["id", "slug"]
        extra_kwargs = {
            "name": {"required": False},
            "start": {"required": False},
            "end": {"required": False},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        service = SchedulingService(user=getattr(request, "user", None))
        try:
            return service.schedule_attendee_enrollment(**validated_data)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)
