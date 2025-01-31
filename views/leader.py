# enrollment/views/leader.py

from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib.auth import get_user_model

from core.views.base import (
    BaseTableListView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseUpdateView,
)
from user.models import User
from enrollment.tables.leader import LeaderEnrollmentTable
from enrollment.models.leader import LeaderEnrollment
from enrollment.serializers import LeaderEnrollmentSerializer
from enrollment.forms.leader import LeaderEnrollmentForm

User = get_user_model()


class IndexView(BaseTableListView):
    model = LeaderEnrollment
    table_class = LeaderEnrollmentTable
    template_name = "leader-enrollment/list.html"

    context_object_name = "leader_enrollments"
    paginate_by = 10

    def get_queryset(self):
        queryset = LeaderEnrollment.objects.all()

        # Check if 'leader_slug' is present in the URL
        leader_slug = self.kwargs.get("leader_slug")
        if leader_slug:
            queryset = queryset.filter(leader__slug=leader_slug)

        return queryset


class ShowView(BaseDetailView):
    model = LeaderEnrollment
    template_name = "leader-enrollment/show.html"
    context_object_name = "leader_enrollment"


class CreateView(LoginRequiredMixin, BaseCreateView):
    model = LeaderEnrollment
    form_class = LeaderEnrollmentForm
    template_name = "leader-enrollment/form.html"

    def get_success_url(self):
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )


class UpdateView(LoginRequiredMixin, BaseUpdateView):
    model = LeaderEnrollment
    form_class = LeaderEnrollmentForm
    template_name = "leader_enrollment/form.html"
    action = "Edit"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )


class DeleteView(BaseDeleteView):
    model = LeaderEnrollment
    template_name = "leader-enrollment/confirm_delete.html"
    action = "Delete"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )


class LeaderEnrollmenyViewSet(viewsets.ModelViewSet):
    queryset = LeaderEnrollment.objects.all()
    serializer_class = LeaderEnrollmentSerializer
