# enrollment/urls.py

from django.urls import path, include

app_name = "enrollments"

urlpatterns = [
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
        "enrollments/organizations/",
        include("enrollment.urls.organization", namespace="organization"),
    ),
    path("weeks/", include("enrollment.urls.week", namespace="week")),
    path("periods/", include("enrollment.urls.period", namespace="period")),
]