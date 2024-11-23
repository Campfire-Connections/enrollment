# enrollment/views/temporal.py

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from ..models.temporal import Week, Period
from ..models.faction import FactionEnrollment
from ..models.facility import FacilityEnrollment
from ..tables.temporal import PeriodTable
from ..forms.period import PeriodForm
from pages.mixins.forms import (
    FormValidMixin, SuccessMessageMixin, ErrorMessageMixin,
    ConditionalRedirectMixin, PrefillFormMixin, ValidationErrorMixin
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django_tables2 import MultiTableMixin
from django_tables2.config import RequestConfig
from facility.models.quarters import Quarters, QuartersType
from facility.models.facility import Facility
from django.http import JsonResponse


def load_weeks(request):
    facility_enrollment_id = request.GET.get("facility_enrollment")
    weeks =Week.objects.filter(facility_enrollment_id=facility_enrollment_id).all()
    return JsonResponse(list(weeks.values("id", "name")), safe=False)


def load_quarters(request):
    week_id = request.GET.get("week")
    facility_enrollment_id = request.GET.get("facility_enrollment")

    # Fetch the facility enrollment and the associated facility
    facility_enrollment = FacilityEnrollment.objects.get(id=facility_enrollment_id)
    facility = facility_enrollment.facility

    # Fetch the QuartersType object that corresponds to 'faction'
    faction_quarters_type = QuartersType.objects.get(slug="faction")

    # Get all quarters of the type 'faction' for the facility
    available_quarters = Quarters.objects.filter(
        facility=facility, type=faction_quarters_type
    )
    print(available_quarters)
    # Find quarters already assigned for this week within the same facility enrollment
    used_quarters = FactionEnrollment.objects.filter(
        week_id=week_id,
        week__facility_enrollment=facility_enrollment,  # Correct relationship through 'week'
    ).values_list("quarters_id", flat=True)

    # Exclude quarters that are already assigned
    available_quarters = available_quarters.exclude(id__in=used_quarters)

    # Return the available quarters as a JSON response
    return JsonResponse(list(available_quarters.values("id", "name")), safe=False)


class WeekManageView(
    LoginRequiredMixin, UserPassesTestMixin, MultiTableMixin, TemplateView
):
    template_name = "week/manage.html"
    enrollment = None
    facility = None
    week = None

    def get_tables(self):
        week = self.get_week()

        # Construct querystrings
        periods_qs = Period.objects.filter(week=week)

        # Build tables with querystrings
        period_table = PeriodTable(periods_qs)

        # Configure tables with pagination and sorting
        RequestConfig(self.request, paginate={"per_page": 8}).configure(period_table)

        return [
            period_table,
        ]

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        facility = self.get_facility()
        enrollment = self.get_enrollment()
        week = self.get_week()

        tables_with_names = [
            {
                "table": table,
                "name": table.Meta.model._meta.verbose_name_plural,
                "create_url": table.get_url(
                    "add",
                    context={
                        "facility_slug": facility.slug,
                        "facility_enrollment_slug": enrollment.slug,
                        "week_slug": week.slug,
                    },
                ),
                "icon": getattr(table, "add_icon", None),
            }
            for table in self.get_tables()
        ]
        context.update(
            {
                "tables_with_names": tables_with_names,
                "facility": facility,
                "enrollment": enrollment,
                "week": week,
            }
        )

        return context

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

    def test_func(self):
        # Check if the user is a faculty member with admin privileges
        return self.request.user.user_type == "FACULTY" and self.request.user.is_admin


class WeekIndexView(ListView):
    model = Week
    template_name = "week/index.html"
    context_object_name = "weeks"


class WeekShowView(DetailView):
    model = Week
    template_name = "week/show.html"
    context_object_name = "week"


class WeekCreateView(CreateView):
    model = Week
    fields = ["name", "start", "end", "facility_enrollment"]
    template_name = "week/form.html"
    success_url = reverse_lazy("week:index")


class WeekUpdateView(UpdateView):
    model = Week
    fields = ["name", "start", "end", "facility_enrollment"]
    template_name = "week/form.html"
    success_url = reverse_lazy("week:index")


class WeekDeleteView(DeleteView):
    model = Week
    template_name = "week/confirm_delete.html"
    success_url = reverse_lazy("week:index")


# Similar views for Period
class PeriodIndexView(ListView):
    model = Period
    template_name = "period/index.html"
    context_object_name = "periods"


class PeriodShowView(DetailView):
    model = Period
    template_name = "period/show.html"
    context_object_name = "period"


class PeriodCreateView(
    FormValidMixin,
    SuccessMessageMixin,
    ErrorMessageMixin,
    ValidationErrorMixin,
    PrefillFormMixin,
    CreateView
):
    model = Period
    form_class = PeriodForm
    template_name = 'period/form.html'
    success_message = "Period successfully created."
    error_message = "There was an error creating the period."

    def get_initial(self):
        """Prefill initial data."""
        initial = super().get_initial()
        week_slug = self.kwargs.get('week_slug')
        if week_slug:
            week = get_object_or_404(Week, slug=week_slug)
            initial['week'] = week
        return initial

    def get_form_kwargs(self):
        """Pass the week instance to the form if slug is available."""
        kwargs = super().get_form_kwargs()
        week_slug = self.kwargs.get('week_slug')
        if week_slug:
            kwargs['week'] = get_object_or_404(Week, slug=week_slug)
        return kwargs

    def get_success_url(self):
        """Redirect to the manage view for the associated week."""
        week_slug = self.kwargs.get('week_slug')
        return reverse('enrollment:weeks:manage', kwargs={'week_slug': week_slug})

    def get_context_data(self, **kwargs):
        """Add extra context for the template."""
        context = super().get_context_data(**kwargs)
        week_slug = self.kwargs.get('week_slug')
        if week_slug:
            context['week'] = get_object_or_404(Week, slug=week_slug)
        return context


class PeriodUpdateView(UpdateView):
    model = Period
    fields = ["name", "start", "end", "week"]
    template_name = "period/form.html"
    success_url = reverse_lazy("period:index")


class PeriodDeleteView(DeleteView):
    model = Period
    template_name = "period/confirm_delete.html"
    success_url = reverse_lazy("period:index")
