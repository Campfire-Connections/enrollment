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
    path("", ActiveEnrollmentIndexView.as_view(), name="index"),
    path("new/", ActiveEnrollmentCreateView.as_view(), name="new"),
    path("<int:pk>/", ActiveEnrollmentShowView.as_view(), name="show"),
    path("<slug:slug>/", ActiveEnrollmentShowView.as_view(), name="show"),
    path("<int:pk>/edit/", ActiveEnrollmentUpdateView.as_view(), name="edit"),
    path("<slug:slug>/edit/", ActiveEnrollmentUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", ActiveEnrollmentDeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", ActiveEnrollmentDeleteView.as_view(), name="delete"),
]
