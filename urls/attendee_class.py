# enrollment/urls/attendee_class.py

from django.urls import path
from ..views.faction import (
    AttendeeClassEnrollmentIndexView,
    AttendeeClassEnrollmentShowView,
    AttendeeClassEnrollmentCreateView,
    AttendeeClassEnrollmentUpdateView,
    AttendeeClassEnrollmentDeleteView,
)

app_name = "enrollments"

urlpatterns = [
    # Attendee Class Enrollment URLs
    path(
        "",
        AttendeeClassEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "new/",
        AttendeeClassEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "<int:pk>/",
        AttendeeClassEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<slug:slug>/",
        AttendeeClassEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<int:pk>/update/",
        AttendeeClassEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "<slug:slug>/update/",
        AttendeeClassEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "<int:pk>/delete/",
        AttendeeClassEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:slug>/delete/",
        AttendeeClassEnrollmentDeleteView.as_view(),
        name="delete",
    ),
]
