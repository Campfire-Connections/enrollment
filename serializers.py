""" Enrollment Model Serializers. """

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


class AttendeeEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendeeEnrollment
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        service = SchedulingService(user=getattr(request, "user", None))
        return service.schedule_attendee_enrollment(**validated_data)
