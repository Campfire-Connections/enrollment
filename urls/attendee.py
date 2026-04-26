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
        "",
        AttendeeEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "new/",
        AttendeeEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "<int:pk>/",
        AttendeeEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<slug:slug>/",
        AttendeeEnrollmentShowView.as_view(),
        name="show",
    ),
    path("<int:pk>/update/", AttendeeEnrollmentUpdateView.as_view(), name="update"),
    path("<slug:slug>/update/", AttendeeEnrollmentUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", AttendeeEnrollmentDeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", AttendeeEnrollmentDeleteView.as_view(), name="delete"),
]
