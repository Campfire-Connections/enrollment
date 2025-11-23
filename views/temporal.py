# enrollment/views/temporal.py

from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from core.views.base import (
    BaseManageView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseTableListView,
    BaseUpdateView,
    build_tables_from_config,
)
from core.mixins.views import LoginRequiredMixin, PortalPermissionMixin
from core.utils import is_faculty_admin

from ..models.temporal import Week, Period
from ..models.faction import FactionEnrollment
from ..models.facility import FacilityEnrollment
from ..tables.week import WeekTable
from ..tables.period import PeriodsByWeekTable, PeriodTable
from ..tables.faction import FactionEnrollmentTable
from ..forms.period import PeriodForm

from facility.models.quarters import Quarters, QuartersType
from facility.models.facility import Facility


def load_weeks(request):
    facility_enrollment_id = request.GET.get("facility_enrollment")
    weeks = Week.objects.filter(facility_enrollment_id=facility_enrollment_id).all()
    return JsonResponse(list(weeks.values("id", "name")), safe=False)


def load_quarters(request):
    week_id = request.GET.get("week")
    facility_enrollment_id = request.GET.get("facility_enrollment")

    facility_enrollment = FacilityEnrollment.objects.get(id=facility_enrollment_id)
    facility = facility_enrollment.facility

    faction_quarters_type = QuartersType.objects.get(slug="faction")

    available_quarters = Quarters.objects.filter(
        facility=facility,
        type=faction_quarters_type,
    )

    used_quarters = FactionEnrollment.objects.filter(
        week_id=week_id,
        week__facility_enrollment=facility_enrollment,
    ).values_list("quarters_id", flat=True)

    available_quarters = available_quarters.exclude(id__in=used_quarters)

    return JsonResponse(list(available_quarters.values("id", "name")), safe=False)


class WeekManageView(LoginRequiredMixin, PortalPermissionMixin, BaseManageView):
    template_name = "week/manage.html"
    enrollment = None
    facility = None
    week = None
    allowed_user_types = ("FACULTY",)

    def test_func(self):
        # Check if the user is a faculty member with admin privileges
        return super().test_func() and is_faculty_admin(self.request.user)

    def get_tables_config(self):
        week = self.get_week()
        return {
            "periods": {
                "class": PeriodsByWeekTable,
                "queryset": Period.objects.filter(week=week),
                "paginate_by": 5,
            },
            "faction_enrollments": {
                "class": FactionEnrollmentTable,
                "queryset": FactionEnrollment.objects.filter(week=week),
                "paginate_by": 10,
            },
        }

    def get_facility(self):
        if self.facility is None:
            facility_slug = self.kwargs.get("facility_slug")
            self.facility = get_object_or_404(Facility, slug=facility_slug)
        return self.facility

    def get_enrollment(self):
        if self.enrollment is None:
            enrollment_slug = self.kwargs.get("facility_enrollment_slug")
            self.enrollment = get_object_or_404(
                FacilityEnrollment, slug=enrollment_slug
            )
        return self.enrollment

    def get_week(self):
        if self.week is None:
            week_slug = self.kwargs.get("week_slug")
            self.week = get_object_or_404(Week, slug=week_slug)
        return self.week


class WeekIndexView(BaseTableListView):
    model = Week
    template_name = "week/index.html"
    context_object_name = "weeks"
    table_class = WeekTable


class WeekShowView(BaseDetailView):
    model = Week
    template_name = "week/show.html"
    context_object_name = "week"
    slug_field = "slug"
    slug_url_kwarg = "week_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            build_tables_from_config(
                self.request,
                {
                    "periods_table": {
                        "class": PeriodTable,
                        "queryset": Period.objects.filter(week=self.get_object()),
                        "paginate_by": None,
                    }
                },
                default_paginate=None,
            )
        )
        return context


class WeekCreateView(BaseCreateView):
    model = Week
    fields = ["name", "start", "end", "facility_enrollment"]
    template_name = "week/form.html"
    success_url = reverse_lazy("weeks:index")


class WeekUpdateView(BaseUpdateView):
    model = Week
    fields = ["name", "start", "end", "facility_enrollment"]
    template_name = "week/form.html"
    success_url = reverse_lazy("weeks:index")


class WeekDeleteView(BaseDeleteView):
    model = Week
    template_name = "week/confirm_delete.html"
    success_url = reverse_lazy("weeks:index")


class PeriodIndexView(BaseTableListView):
    model = Period
    template_name = "period/index.html"
    context_object_name = "periods"


class PeriodShowView(BaseDetailView):
    model = Period
    template_name = "period/show.html"
    context_object_name = "period"
    slug_field = "slug"
    slug_url_kwarg = "period_slug"


class PeriodCreateView(BaseCreateView):
    model = Period
    form_class = PeriodForm
    template_name = "period/form.html"
    success_message = "Period successfully created."
    error_message = "There was an error creating the period."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        facility = get_object_or_404(Facility, slug=self.kwargs.get("facility_slug"))
        facility_enrollment = get_object_or_404(
            FacilityEnrollment, slug=self.kwargs.get("facility_enrollment_slug")
        )
        week = get_object_or_404(Week, slug=self.kwargs.get("week_slug"))

        kwargs.update(
            {
                "facility": facility,
                "facility_enrollment": facility_enrollment,
                "week": week,
            }
        )
        return kwargs

    def get_success_url(self):
        week_slug = self.kwargs.get("week_slug")
        return reverse("enrollments:weeks:manage", kwargs={"week_slug": week_slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_slug = self.kwargs.get("week_slug")
        if week_slug:
            context["week"] = get_object_or_404(Week, slug=week_slug)
        return context

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PeriodUpdateView(BaseUpdateView):
    model = Period
    fields = ["name", "start", "end", "week"]
    template_name = "period/form.html"
    success_url = reverse_lazy("periods:index")


class PeriodDeleteView(BaseDeleteView):
    model = Period
    template_name = "period/confirm_delete.html"
    success_url = reverse_lazy("periods:index")
