# enrollment/views/leader.py

from rest_framework import viewsets
from django.urls import reverse

from core.views.base import (
    BaseTableListView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseUpdateView,
)
from core.mixins.views import LoginRequiredMixin

from enrollment.tables.leader import LeaderEnrollmentTable
from enrollment.models.leader import LeaderEnrollment
from enrollment.serializers import LeaderEnrollmentSerializer
from enrollment.forms.leader import LeaderEnrollmentForm
from enrollment.services import SchedulingService
from enrollment.mixin import SchedulingServiceFormMixin
from core.api import BaseModelViewSet


class IndexView(BaseTableListView):
    model = LeaderEnrollment
    table_class = LeaderEnrollmentTable
    template_name = "leader-enrollment/list.html"
    context_object_name = "leader_enrollments"
    paginate_by = 10

    def get_queryset(self):
        queryset = LeaderEnrollment.objects.with_related()
        leader_slug = self.kwargs.get("leader_slug")
        if leader_slug:
            queryset = queryset.filter(leader__slug=leader_slug)
        return queryset


class ShowView(BaseDetailView):
    model = LeaderEnrollment
    template_name = "leader-enrollment/show.html"
    context_object_name = "leader_enrollment"


class CreateView(LoginRequiredMixin, SchedulingServiceFormMixin, BaseCreateView):
    model = LeaderEnrollment
    form_class = LeaderEnrollmentForm
    template_name = "leader-enrollment/form.html"
    service_class = SchedulingService
    service_method = "schedule_leader_enrollment"

    def get_success_url(self):
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )


class UpdateView(LoginRequiredMixin, SchedulingServiceFormMixin, BaseUpdateView):
    model = LeaderEnrollment
    form_class = LeaderEnrollmentForm
    template_name = "leader_enrollment/form.html"
    action = "Edit"
    service_class = SchedulingService
    service_method = "schedule_leader_enrollment"

    def get_success_url(self):
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        kwargs = super().get_service_kwargs(form)
        kwargs["leader_enrollment"] = self.object
        return kwargs


class DeleteView(BaseDeleteView):
    model = LeaderEnrollment
    template_name = "leader-enrollment/confirm_delete.html"
    action = "Delete"

    def get_success_url(self):
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:leaders:enrollments:index",
            kwargs={
                "faction_slug": faction_slug,
                "leader_slug": self.object.leader.slug,
            },
        )


class LeaderEnrollmenyViewSet(BaseModelViewSet):
    queryset = LeaderEnrollment.objects.with_related()
    serializer_class = LeaderEnrollmentSerializer
