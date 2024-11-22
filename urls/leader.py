# enrollment/urls/leader.py

from django.urls import path

from ..views.faction import (
    LeaderEnrollmentIndexView,
    LeaderEnrollmentShowView,
    LeaderEnrollmentCreateView,
    LeaderEnrollmentUpdateView,
    LeaderEnrollmentDeleteView,
)

app_name = "leader"

urlpatterns = [
    # Leader Enrollment URLs
    path(
        "enrollments/leaders/",
        LeaderEnrollmentIndexView.as_view(),
        name="leader_enrollment_index",
    ),
    path(
        "enrollments/leaders/create/",
        LeaderEnrollmentCreateView.as_view(),
        name="leader_enrollment_create",
    ),
    path(
        "enrollments/leaders/<int:pk>/",
        LeaderEnrollmentShowView.as_view(),
        name="leader_enrollment_show",
    ),
    path(
        "enrollments/leaders/<slug:slug>/",
        LeaderEnrollmentShowView.as_view(),
        name="leader_enrollment_show",
    ),
    path(
        "enrollments/leaders/<int:pk>/update/",
        LeaderEnrollmentUpdateView.as_view(),
        name="leader_enrollment_update",
    ),
    path(
        "enrollments/leaders/<slug:slug>/update/",
        LeaderEnrollmentUpdateView.as_view(),
        name="leader_enrollment_update",
    ),
    path(
        "enrollments/leaders/<int:pk>/delete/",
        LeaderEnrollmentDeleteView.as_view(),
        name="leader_enrollment_delete",
    ),
    path(
        "enrollments/leaders/<slug:slug>/delete/",
        LeaderEnrollmentDeleteView.as_view(),
        name="leader_enrollment_delete",
    ),
]