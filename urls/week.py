# enrollment/urls/week.py

from django.urls import path, include

from ..views.temporal import (
    WeekIndexView,
    WeekShowView,
    WeekCreateView,
    WeekUpdateView,
    WeekDeleteView,
    WeekManageView,
)

app_name = "weeks"

urlpatterns = [
    # Week URLs
    path("", WeekIndexView.as_view(), name="index"),
    path("new/", WeekCreateView.as_view(), name="new"),
    path("<int:pk>/", WeekShowView.as_view(), name="show"),
    path("<slug:week_slug>/", WeekShowView.as_view(), name="show"),
    path("<int:pk>/update/", WeekUpdateView.as_view(), name="update"),
    path("<slug:week_slug>/update/", WeekUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", WeekDeleteView.as_view(), name="delete"),
    path("<slug:week_slug>/delete/", WeekDeleteView.as_view(), name="delete"),
    path("manage/", WeekManageView.as_view(), name="manage"),
    path(
        "<slug:week_slug>/periods/",
        include("enrollment.urls.period", namespace="periods"),
    ),
]
