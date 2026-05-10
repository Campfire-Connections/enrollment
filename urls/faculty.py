# enrollment/urls/faculty.py

from django.urls import path

from ..views.facility import (
    FacultyEnrollmentIndexView,
    FacultyEnrollmentShowView,
    FacultyEnrollmentCreateView,
    FacultyEnrollmentUpdateView,
    FacultyEnrollmentDeleteView,
)
from ..views.facility import (
    FacultyClassEnrollmentIndexView,
    FacultyClassEnrollmentShowView,
    FacultyClassEnrollmentCreateView,
    FacultyClassEnrollmentUpdateView,
    FacultyClassEnrollmentDeleteView,
)


app_name = "faculty"

urlpatterns = [
    path("", FacultyEnrollmentIndexView.as_view(), name="index"),
    path("new/", FacultyEnrollmentCreateView.as_view(), name="new"),
    path("<int:pk>/", FacultyEnrollmentShowView.as_view(), name="show"),
    path("<slug:faculty_enrollment_slug>/", FacultyEnrollmentShowView.as_view(), name="show"),
    path("<int:pk>/update/", FacultyEnrollmentUpdateView.as_view(), name="edit"),
    path(
        "<slug:faculty_enrollment_slug>/update/",
        FacultyEnrollmentUpdateView.as_view(),
        name="edit",
    ),
    path("<int:pk>/delete/", FacultyEnrollmentDeleteView.as_view(), name="delete"),
    path(
        "<slug:faculty_enrollment_slug>/delete/",
        FacultyEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path("classes/", FacultyClassEnrollmentIndexView.as_view(), name="class_index"),
    path("classes/new/", FacultyClassEnrollmentCreateView.as_view(), name="class_new"),
    path("classes/<int:pk>/", FacultyClassEnrollmentShowView.as_view(), name="class_show"),
    path(
        "classes/<slug:faculty_class_enrollment_slug>/",
        FacultyClassEnrollmentShowView.as_view(),
        name="class_show",
    ),
    path(
        "classes/<int:pk>/update/",
        FacultyClassEnrollmentUpdateView.as_view(),
        name="class_edit",
    ),
    path(
        "classes/<slug:faculty_class_enrollment_slug>/update/",
        FacultyClassEnrollmentUpdateView.as_view(),
        name="class_edit",
    ),
    path(
        "classes/<int:pk>/delete/",
        FacultyClassEnrollmentDeleteView.as_view(),
        name="class_delete",
    ),
    path(
        "classes/<slug:faculty_class_enrollment_slug>/delete/",
        FacultyClassEnrollmentDeleteView.as_view(),
        name="class_delete",
    ),
]
