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
    # Faculty Enrollment URLs
    path(
        "enrollments/faculty/",
        FacultyEnrollmentIndexView.as_view(),
        name="index",
    ),
    path(
        "enrollments/faculty/create/",
        FacultyEnrollmentCreateView.as_view(),
        name="new",
    ),
    path(
        "enrollments/faculty/<int:pk>/",
        FacultyEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "enrollments/faculty/<slug:slug>/",
        FacultyEnrollmentShowView.as_view(),
        name="show",
    ),
    path(
        "enrollments/faculty/<int:pk>/update/",
        FacultyEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "enrollments/faculty/<slug:slug>/update/",
        FacultyEnrollmentUpdateView.as_view(),
        name="update",
    ),
    path(
        "enrollments/faculty/<int:pk>/delete/",
        FacultyEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    path(
        "enrollments/faculty/<slug:slug>/delete/",
        FacultyEnrollmentDeleteView.as_view(),
        name="delete",
    ),
    # Faculty Class Enrollment URLs
    path(
        "enrollments/classes/faculty/",
        FacultyClassEnrollmentIndexView.as_view(),
        name="faculty_class_enrollment_index",
    ),
    path(
        "enrollments/classes/faculty/create/",
        FacultyClassEnrollmentCreateView.as_view(),
        name="faculty_class_enrollment_create",
    ),
    path(
        "enrollments/classes/faculty/<int:pk>/",
        FacultyClassEnrollmentShowView.as_view(),
        name="faculty_class_enrollment_show",
    ),
    path(
        "enrollments/classes/faculty/<slug:slug>/",
        FacultyClassEnrollmentShowView.as_view(),
        name="faculty_class_enrollment_show",
    ),
    path(
        "enrollments/classes/faculty/<int:pk>/edit/",
        FacultyClassEnrollmentUpdateView.as_view(),
        name="faculty_class_enrollment_edit",
    ),
    path(
        "enrollments/classes/faculty/<slug:slug>/edit/",
        FacultyClassEnrollmentUpdateView.as_view(),
        name="faculty_class_enrollment_edit",
    ),
    path(
        "enrollments/classes/faculty/<int:pk>/delete/",
        FacultyClassEnrollmentDeleteView.as_view(),
        name="faculty_class_enrollment_delete",
    ),
    path(
        "enrollments/classes/faculty/<slug:slug>/delete/",
        FacultyClassEnrollmentDeleteView.as_view(),
        name="faculty_class_enrollment_delete",
    ),
]