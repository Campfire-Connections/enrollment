""" Enrollment Model Serializers. """

from rest_framework import serializers

from enrollment.models.faction import FactionEnrollment
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.attendee import AttendeeEnrollment


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
