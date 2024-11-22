# enrollment/urls/faction.py

from django.urls import path
from ..views.faction import (
    FactionEnrollmentIndexView,
    FactionEnrollmentShowView,
    FactionEnrollmentCreateView,
    FactionEnrollmentUpdateView,
    FactionEnrollmentDeleteView,
)

app_name = "enrollments"

urlpatterns = [
    # Faction Enrollment URLs
    path(
        "",
        FactionEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "new/",
        FactionEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "<int:enrollment_pk>/",
        FactionEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<slug:enrollment_slug>/",
        FactionEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<int:enrollment_pk>/update/",
        FactionEnrollmentUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<slug:enrollment_slug>/update/",
        FactionEnrollmentUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:enrollment_pk>/delete/",
        FactionEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:enrollment_slug>/delete/",
        FactionEnrollmentDeleteView.as_view(),
        name="delete",
    ),
]
