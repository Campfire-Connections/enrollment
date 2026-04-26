# enrollment/urls/__init__.py

from django.urls import path, include
from ..views.temporal import load_weeks, load_quarters
from enrollment.views.availability import AvailabilityDashboardView, AvailabilityHoldView
from enrollment.views.enrollment import MyScheduleView

app_name = "enrollments"

urlpatterns = [
    path(
        "enrollments/availability/",
        AvailabilityDashboardView.as_view(),
        name="availability",
    ),
    path(
        "enrollments/availability/<str:kind>/<int:pk>/hold/",
        AvailabilityHoldView.as_view(),
        name="availability_hold",
    ),
    path("enrollments/my-schedule/", MyScheduleView.as_view(), name="my_schedule"),
    path(
        "enrollments/facilities/",
        include("enrollment.urls.facility", namespace="facility"),
    ),
    path(
        "enrollments/factions/", include("enrollment.urls.faction", namespace="faction")
    ),
    path(
        "enrollments/faculty/", include("enrollment.urls.faculty", namespace="faculty")
    ),
    path("enrollments/leaders/", include("enrollment.urls.leader", namespace="leader")),
    path(
        "enrollments/attendees/",
        include("enrollment.urls.attendee", namespace="attendee"),
    ),
    path(
        "enrollments/attendee-classes/",
        include("enrollment.urls.attendee_class", namespace="attendee_class"),
    ),
    path(
        "enrollments/organizations/",
        include("enrollment.urls.organization", namespace="organization"),
    ),
    path("weeks/", include("enrollment.urls.week", namespace="week")),
    path("periods/", include("enrollment.urls.period", namespace="period")),
    path('ajax/load-weeks/', load_weeks, name='ajax_load_weeks'),
    path('ajax/load-quarters/', load_quarters, name='ajax_load_quarters'),
]
