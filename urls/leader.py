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
    path("", IndexView.as_view(), name="index"),
    path("new/", CreateView.as_view(), name="new"),
    path("<int:pk>/", ShowView.as_view(), name="show"),
    path("<slug:slug>/", ShowView.as_view(), name="show"),
    path("<int:pk>/update/", UpdateView.as_view(), name="edit"),
    path("<slug:slug>/update/", UpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", DeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", DeleteView.as_view(), name="delete"),
]
