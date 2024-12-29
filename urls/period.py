# enrollment/urls/period.py

from django.urls import path

from ..views.temporal import (
    PeriodIndexView,
    PeriodShowView,
    PeriodCreateView,
    PeriodUpdateView,
    PeriodDeleteView,
)

app_name = "periods"

urlpatterns = [
    # Period URLs
    path("", PeriodIndexView.as_view(), name="index"),
    path("new/", PeriodCreateView.as_view(), name="new"),
    path("<int:pk>/", PeriodShowView.as_view(), name="show"),
    path("<slug:period_slug>/", PeriodShowView.as_view(), name="show"),
    path("<int:pk>/update/", PeriodUpdateView.as_view(), name="edit"),
    path("<slug:period_slug>/update/", PeriodUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", PeriodDeleteView.as_view(), name="delete"),
    path(
        "<slug:period_slug>/delete/", PeriodDeleteView.as_view(), name="delete"
    ),
]
