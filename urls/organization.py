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
    path("", OrganizationEnrollmentIndexView.as_view(), name="index"),
    path("new/", OrganizationEnrollmentCreateView.as_view(), name="new"),
    path("<int:pk>/", OrganizationEnrollmentShowView.as_view(), name="show"),
    path("<slug:slug>/", OrganizationEnrollmentShowView.as_view(), name="show"),
    path("<int:pk>/update/", OrganizationEnrollmentUpdateView.as_view(), name="edit"),
    path("<slug:slug>/update/", OrganizationEnrollmentUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", OrganizationEnrollmentDeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", OrganizationEnrollmentDeleteView.as_view(), name="delete"),
    path("courses/", OrganizationCourseIndexView.as_view(), name="course_index"),
    path("courses/new/", OrganizationCourseCreateView.as_view(), name="course_new"),
    path("courses/<int:pk>/", OrganizationCourseShowView.as_view(), name="course_show"),
    path("courses/<slug:slug>/", OrganizationCourseShowView.as_view(), name="course_show"),
    path(
        "courses/<int:pk>/update/",
        OrganizationCourseUpdateView.as_view(),
        name="course_edit",
    ),
    path(
        "courses/<slug:slug>/update/",
        OrganizationCourseUpdateView.as_view(),
        name="course_edit",
    ),
    path(
        "courses/<int:pk>/delete/",
        OrganizationCourseDeleteView.as_view(),
        name="course_delete",
    ),
    path(
        "courses/<slug:slug>/delete/",
        OrganizationCourseDeleteView.as_view(),
        name="course_delete",
    ),
]
