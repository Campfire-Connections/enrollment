# enrollment/urls/facility.py

from django.urls import path, include
from ..views.facility import (
    FacilityEnrollmentIndexView,
    FacilityEnrollmentShowView,
    FacilityEnrollmentCreateView,
    FacilityEnrollmentUpdateView,
    FacilityEnrollmentDeleteView,
    FacilityEnrollmentManageView
)


app_name = "enrollments"

urlpatterns = [
    # Facility Enrollment URLs
    path(
        "",
        FacilityEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "new/",
        FacilityEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "<int:pk>/",
        FacilityEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<slug:facility_enrollment_slug>/",
        FacilityEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "<int:pk>/update/",
        FacilityEnrollmentUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<slug:facility_enrollment_slug>/update/",
        FacilityEnrollmentUpdateView.as_view(),
        name="edit",
    ),
    path(
        "<int:pk>/delete/",
        FacilityEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:facility_enrollment_slug>/delete/",
        FacilityEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<slug:facility_enrollment_slug>/manage/",
        FacilityEnrollmentManageView.as_view(),
        name="manage",
    ),
    path(
        "<slug:facility_enrollment_slug>/weeks/",
        include("enrollment.urls.week", namespace="weeks"),
    ),
]
