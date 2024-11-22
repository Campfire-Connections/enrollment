# enrollment/urls/enrollment.py

from django.urls import path
from ..views.enrollment import (
    ActiveEnrollmentIndexView,
    ActiveEnrollmentShowView,
    ActiveEnrollmentCreateView,
    ActiveEnrollmentUpdateView,
    ActiveEnrollmentDeleteView,
    MyScheduleView
)

app_name = "enrollment"

urlpatterns = [
    path(
        "enrollments/active/",
        ActiveEnrollmentIndexView.as_view(),
        name="active_enrollment_index",
    ),
    path(
        "enrollments/active/create/",
        ActiveEnrollmentCreateView.as_view(),
        name="active_enrollment_create",
    ),
    path(
        "enrollments/active/<int:pk>/",
        ActiveEnrollmentShowView.as_view(),
        name="active_enrollment_show",
    ),
    path(
        "enrollments/active/<slug:slug>/",
        ActiveEnrollmentShowView.as_view(),
        name="active_enrollment_show",
    ),
    path(
        "enrollments/active/<int:pk>/edit/",
        ActiveEnrollmentUpdateView.as_view(),
        name="active_enrollment_edit",
    ),
    path(
        "enrollments/active/<slug:slug>/edit/",
        ActiveEnrollmentUpdateView.as_view(),
        name="active_enrollment_edit",
    ),
    path(
        "enrollments/active/<int:pk>/delete/",
        ActiveEnrollmentDeleteView.as_view(),
        name="active_enrollment_delete",
    ),
    path(
        "enrollments/active/<slug:slug>/delete/",
        ActiveEnrollmentDeleteView.as_view(),
        name="active_enrollment_delete",
    ),
    path('my-schedule/', MyScheduleView.as_view(), name='my_schedule'),
]
