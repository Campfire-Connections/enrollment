# enrollment/urls/organization.py

from django.urls import path
from ..views.organization import (
    OrganizationEnrollmentIndexView,
    OrganizationEnrollmentShowView,
    OrganizationEnrollmentCreateView,
    OrganizationEnrollmentUpdateView,
    OrganizationEnrollmentDeleteView,
)
from ..views.organization import (
    OrganizationCourseIndexView,
    OrganizationCourseShowView,
    OrganizationCourseCreateView,
    OrganizationCourseUpdateView,
    OrganizationCourseDeleteView,
)

app_name = "organization"

urlpatterns = [
    # Organization Enrollment URLs
    path(
        "enrollments/organizations//",
        OrganizationEnrollmentIndexView.as_view(),
        name="organization_enrollment_index",
    ),
    path(
        "enrollments/organizations//create/",
        OrganizationEnrollmentCreateView.as_view(),
        name="organization_enrollment_create",
    ),
    path(
        "enrollments/organizations//<int:pk>/",
        OrganizationEnrollmentShowView.as_view(),
        name="organization_enrollment_show",
    ),
    path(
        "enrollments/organizations//<slug:slug>/",
        OrganizationEnrollmentShowView.as_view(),
        name="organization_enrollment_show",
    ),
    path(
        "enrollments/organizations//<int:pk>/update/",
        OrganizationEnrollmentUpdateView.as_view(),
        name="organization_enrollment_update",
    ),
    path(
        "enrollments/organizations//<slug:slug>/update/",
        OrganizationEnrollmentUpdateView.as_view(),
        name="organization_enrollment_update",
    ),
    path(
        "enrollments/organizations//<int:pk>/delete/",
        OrganizationEnrollmentDeleteView.as_view(),
        name="organization_enrollment_delete",
    ),
    path(
        "enrollments/organizations//<slug:slug>/delete/",
        OrganizationEnrollmentDeleteView.as_view(),
        name="organization_enrollment_delete",
    ),
    # Organization Course URLs
    path(
        "courses/organizations/",
        OrganizationCourseIndexView.as_view(),
        name="organization_course_index",
    ),
    path(
        "courses/organizations/create/",
        OrganizationCourseCreateView.as_view(),
        name="organization_course_create",
    ),
    path(
        "courses/organizations/<int:pk>/",
        OrganizationCourseShowView.as_view(),
        name="organization_course_show",
    ),
    path(
        "courses/organizations/<slug:slug>/",
        OrganizationCourseShowView.as_view(),
        name="organization_course_show",
    ),
    path(
        "courses/organizations/<int:pk>/update/",
        OrganizationCourseUpdateView.as_view(),
        name="organization_course_update",
    ),
    path(
        "courses/organizations/<slug:slug>/update/",
        OrganizationCourseUpdateView.as_view(),
        name="organization_course_update",
    ),
    path(
        "courses/organizations/<int:pk>/delete/",
        OrganizationCourseDeleteView.as_view(),
        name="organization_course_delete",
    ),
    path(
        "courses/organizations/<slug:slug>/delete/",
        OrganizationCourseDeleteView.as_view(),
        name="organization_course_delete",
    ),
]
