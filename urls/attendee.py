# enrollment/urls/attendee.py

from django.urls import path

from ..views.faction import (
    AttendeeEnrollmentIndexView,
    AttendeeEnrollmentShowView,
    AttendeeEnrollmentCreateView,
    AttendeeEnrollmentUpdateView,
    AttendeeEnrollmentDeleteView,
)
from ..views.attendee import AttendeeEnrollmentIndexByAttendeeView

app_name = "enrollments"

urlpatterns = [
    # Attendee Enrollment URLs
    path(
        "<int:pk>/enrollments/",
        AttendeeEnrollmentIndexByAttendeeView.as_view(),
        name="index_by_attendee",
    ),
    path(
        "<slug:slug>/enrollments/",
        AttendeeEnrollmentIndexByAttendeeView.as_view(),
        name="index_by_attendee",
    ),
    path(
        "",
        AttendeeEnrollmentIndexView.as_view(),
        name="attendee_enrollment_index",
    ),
    path(
        "create/",
        AttendeeEnrollmentCreateView.as_view(),
        name="attendee_enrollment_create",
    ),
    path(
        "<int:pk>/",
        AttendeeEnrollmentShowView.as_view(),
        name="attendee_enrollment_show",
    ),
    path(
        "<slug:slug>/",
        AttendeeEnrollmentShowView.as_view(),
        name="attendee_enrollment_show",
    ),
    path(
        "<int:pk>/update/",
        AttendeeEnrollmentUpdateView.as_view(),
        name="attendee_enrollment_update",
    ),
    path(
        "<slug:slug>/update/",
        AttendeeEnrollmentUpdateView.as_view(),
        name="attendee_enrollment_update",
    ),
    path(
        "<int:pk>/delete/",
        AttendeeEnrollmentDeleteView.as_view(),
        name="attendee_enrollment_delete",
    ),
    path(
        "<slug:slug>/delete/",
        AttendeeEnrollmentDeleteView.as_view(),
        name="attendee_enrollment_delete",
    ),
]
