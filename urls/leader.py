# enrollment/urls/leader.py

from django.urls import path

from enrollment.views.leader import (
    IndexView,
    ShowView,
    CreateView,
    UpdateView,
    DeleteView,
)

app_name = "enrollments"

urlpatterns = [
    # Leader Enrollment URLs
    path(
        "enrollments/leaders/",
        IndexView.as_view(),
        name="leader_enrollment_index",
    ),
    path(
        "enrollments/leaders/create/",
        CreateView.as_view(),
        name="leader_enrollment_create",
    ),
    path(
        "enrollments/leaders/<int:pk>/",
        ShowView.as_view(),
        name="leader_enrollment_show",
    ),
    path(
        "enrollments/leaders/<slug:slug>/",
        ShowView.as_view(),
        name="leader_enrollment_show",
    ),
    path(
        "enrollments/leaders/<int:pk>/update/",
        UpdateView.as_view(),
        name="leader_enrollment_update",
    ),
    path(
        "enrollments/leaders/<slug:slug>/update/",
        UpdateView.as_view(),
        name="leader_enrollment_update",
    ),
    path(
        "enrollments/leaders/<int:pk>/delete/",
        DeleteView.as_view(),
        name="leader_enrollment_delete",
    ),
    path(
        "enrollments/leaders/<slug:slug>/delete/",
        DeleteView.as_view(),
        name="leader_enrollment_delete",
    ),
]