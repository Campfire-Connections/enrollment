# enrollment/views/faction.py

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from core.mixins.views import LoginRequiredMixin
from core.policies import can_manage_faction

from faction.models.faction import Faction

from ..models.faction import FactionEnrollment
from ..models.leader import LeaderEnrollment
from ..models.attendee import AttendeeEnrollment
from ..models.attendee_class import AttendeeClassEnrollment
from ..models.facility import FacilityEnrollment
from ..forms.faction import FactionEnrollmentForm
from ..forms.attendee import AttendeeClassEnrollmentForm, AttendeeEnrollmentForm
from ..services import SchedulingService
from ..mixin import SchedulingServiceFormMixin
from ..tables.faction import FactionEnrollmentTable
from ..tables.attendee import AttendeeEnrollmentTable
from django_tables2 import SingleTableMixin


class FactionEnrollmentIndexView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = FactionEnrollment
    table_class = FactionEnrollmentTable
    template_name = "faction-enrollment/index.html"
    context_object_name = "faction_enrollments"
    faction = None

    def get_queryset(self):
        qs = FactionEnrollment.objects.with_related()
        slug = self.kwargs.get("faction_slug") or self.kwargs.get("slug")
        if slug:
            self.faction = get_object_or_404(Faction, slug=slug)
            qs = qs.filter(faction=self.faction)
        else:
            profile = getattr(self.request.user, "leaderprofile_profile", None)
            if profile and profile.faction_id:
                self.faction = profile.faction
                qs = qs.filter(faction=self.faction)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faction"] = self.faction
        return context


class FactionEnrollmentShowView(LoginRequiredMixin, DetailView):
    model = FactionEnrollment
    template_name = "faction-enrollment/show.html"
    context_object_name = "faction_enrollment"
    pk_url_kwarg = "enrollment_pk"
    slug_url_kwarg = "enrollment_slug"

    def get_queryset(self):
        return FactionEnrollment.objects.with_related()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_faction_enrollment_page"] = can_manage_faction(
            self.request.user,
            getattr(self.object, "faction", None),
        )
        return context


class FactionEnrollmentCreateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, CreateView
):
    model = FactionEnrollment
    template_name = "faction-enrollment/form.html"
    success_url = reverse_lazy("factions:enrollments:index")
    form_class = FactionEnrollmentForm
    service_class = SchedulingService
    service_method = "schedule_faction_enrollment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faction"] = self._get_faction()
        return context

    def _get_faction(self):
        slug = self.kwargs.get("faction_slug") or self.kwargs.get("slug")
        return get_object_or_404(Faction, slug=slug)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faction"] = self._get_faction()
        return kwargs

    def get_service_kwargs(self, form):
        faction = self._get_faction()
        week = form.cleaned_data["week"]
        return {
            "faction": faction,
            "facility_enrollment": form.cleaned_data["facility_enrollment"],
            "week": week,
            "quarters": form.cleaned_data["quarters"],
            "start": week.start,
            "end": week.end,
            "name": form.instance.name or f"{faction.name} - {week.name}",
            "description": form.instance.description,
        }

    def get_success_url(self):
        return reverse(
            "factions:show", kwargs={"faction_slug": self.object.faction.slug}
        )

class FactionEnrollmentUpdateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, UpdateView
):
    model = FactionEnrollment
    form_class = FactionEnrollmentForm
    template_name = "faction-enrollment/form.html"
    service_class = SchedulingService
    service_method = "schedule_faction_enrollment"
    pk_url_kwarg = "enrollment_pk"
    slug_url_kwarg = "enrollment_slug"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["faction"] = self.get_object().faction
        return kwargs

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        week = form.cleaned_data["week"]
        faction = form.cleaned_data.get("faction") or self.object.faction
        return {
            "faction": faction,
            "facility_enrollment": form.cleaned_data["facility_enrollment"],
            "week": week,
            "quarters": form.cleaned_data["quarters"],
            "start": week.start,
            "end": week.end,
            "name": form.instance.name or f"{faction.name} - {week.name}",
            "description": form.instance.description,
            "faction_enrollment": self.object,
        }

    def get_success_url(self):
        return reverse(
            "factions:show", kwargs={"faction_slug": self.object.faction.slug}
        )


class FactionEnrollmentDeleteView(LoginRequiredMixin, DeleteView):
    model = FactionEnrollment
    template_name = "faction-enrollment/confirm_delete.html"
    pk_url_kwarg = "enrollment_pk"
    slug_url_kwarg = "enrollment_slug"

    def get_success_url(self):
        return reverse(
            "factions:show", kwargs={"faction_slug": self.object.faction.slug}
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        service = SchedulingService(user=getattr(request, "user", None))
        service.drop_faction_enrollment(faction_enrollment=self.object)
        return HttpResponseRedirect(success_url)





class AttendeeEnrollmentIndexView(LoginRequiredMixin, SingleTableMixin, ListView):
    model = AttendeeEnrollment
    table_class = AttendeeEnrollmentTable
    template_name = "attendee-enrollment/list.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        qs = AttendeeEnrollment.objects.with_related()
        attendee_slug = self.kwargs.get("slug")
        if attendee_slug:
            qs = qs.filter(attendee__slug=attendee_slug)
        return qs

class AttendeeEnrollmentIndexByAttendee(LoginRequiredMixin, SingleTableMixin, ListView):
    """Deprecated duplicate; use enrollment.views.attendee.AttendeeEnrollmentIndexByAttendeeView."""

    model = AttendeeEnrollment
    table_class = AttendeeEnrollmentTable
    template_name = "attendee-enrollment/list.html"
    context_object_name = "attendee_enrollments"

    def get_queryset(self):
        qs = AttendeeEnrollment.objects.with_related()
        attendee_slug = self.kwargs.get("slug")
        if attendee_slug:
            qs = qs.filter(attendee__slug=attendee_slug)
        return qs
    
class AttendeeEnrollmentShowView(LoginRequiredMixin, DetailView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/show.html"
    context_object_name = "attendee_enrollment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage_attendee_enrollment_page"] = can_manage_faction(
            self.request.user,
            getattr(getattr(self.object, "faction_enrollment", None), "faction", None),
        )
        return context


class AttendeeEnrollmentCreateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, CreateView
):
    model = AttendeeEnrollment
    form_class = AttendeeEnrollmentForm
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("enrollments:attendee:index")
    service_class = SchedulingService
    service_method = "schedule_attendee_enrollment"


class AttendeeEnrollmentUpdateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, UpdateView
):
    model = AttendeeEnrollment
    form_class = AttendeeEnrollmentForm
    template_name = "attendee-enrollment/form.html"
    success_url = reverse_lazy("enrollments:attendee:index")
    service_method = "schedule_attendee_enrollment"

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        kwargs = super().get_service_kwargs(form)
        kwargs["attendee_enrollment"] = self.object
        return kwargs


class AttendeeEnrollmentDeleteView(LoginRequiredMixin, DeleteView):
    model = AttendeeEnrollment
    template_name = "attendee-enrollment/confirm_delete.html"
    success_url = reverse_lazy("enrollments:attendee:index")


class AttendeeClassEnrollmentIndexView(LoginRequiredMixin, ListView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/list.html"
    context_object_name = "attendee_class_enrollments"


class AttendeeClassEnrollmentShowView(LoginRequiredMixin, DetailView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/show.html"
    context_object_name = "attendee_class_enrollment"


class AttendeeClassEnrollmentCreateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, CreateView
):
    model = AttendeeClassEnrollment
    form_class = AttendeeClassEnrollmentForm
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("enrollments:attendee_class:index")
    service_class = SchedulingService
    service_method = "assign_attendee_to_class"


class AttendeeClassEnrollmentUpdateView(
    LoginRequiredMixin, SchedulingServiceFormMixin, UpdateView
):
    model = AttendeeClassEnrollment
    form_class = AttendeeClassEnrollmentForm
    template_name = "attendee-class-enrollment/form.html"
    success_url = reverse_lazy("enrollments:attendee_class:index")
    service_method = "assign_attendee_to_class"

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        kwargs = super().get_service_kwargs(form)
        kwargs["attendee_class_enrollment"] = self.object
        return kwargs


class AttendeeClassEnrollmentDeleteView(LoginRequiredMixin, DeleteView):
    model = AttendeeClassEnrollment
    template_name = "attendee-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("enrollments:attendee_class:index")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        service = SchedulingService(user=getattr(request, "user", None))
        service.drop_attendee_from_class(attendee_class_enrollment=self.object)
        return HttpResponseRedirect(success_url)
