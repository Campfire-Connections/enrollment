# enrollment/urls/facility_class_enrollment.py

from django.urls import path
from ..views.facility import (
    FacilityClassEnrollmentIndexView,
    FacilityClassEnrollmentShowView,
    FacilityClassEnrollmentCreateView,
    FacilityClassEnrollmentUpdateView,
    FacilityClassEnrollmentDeleteView,
)


app_name = "enrollments"

urlpatterns = [
    # Facility Class Enrollment URLs
    path(
        "",
        FacilityClassEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "new/",
        FacilityClassEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "<int:pk>/",
        FacilityClassEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<slug:slug>/",
        FacilityClassEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<int:pk>/update/",
        FacilityClassEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "<slug:slug>/update/",
        FacilityClassEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "<int:pk>/delete/",
        FacilityClassEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:slug>/delete/",
        FacilityClassEnrollmentDeleteView.as_view(),
        name="delete",
    ),
]
