""" Enrollment Model Serializers. """

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from enrollment.models.faction import FactionEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.services import SchedulingService


class FactionEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactionEnrollment
        fields = "__all__"


class LeaderEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderEnrollment
        fields = "__all__"
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
        fields = "__all__"
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
