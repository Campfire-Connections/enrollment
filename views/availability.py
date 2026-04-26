import csv

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from core.mixins.views import LoginRequiredMixin, StaffRequiredMixin
from enrollment.models.availability import (
    FacilityClassAvailability,
    FacultyQuartersAvailability,
    QuartersWeekAvailability,
)
from enrollment.services.availability import build_availability_status


AVAILABILITY_MODELS = {
    "class": FacilityClassAvailability,
    "faculty_quarters": FacultyQuartersAvailability,
    "faction_quarters": QuartersWeekAvailability,
}


class AvailabilityDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "availability/dashboard.html"

    def get(self, request, *args, **kwargs):
        if request.GET.get("format") == "csv":
            return self._csv_response()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_availability_status())
        return context

    def _csv_response(self):
        status = build_availability_status()
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="availability-health.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(["section", "kind", "label", "expected", "actual"])
        for issue in status["issues"]:
            writer.writerow(
                ["issue", issue.kind, issue.label, issue.expected, issue.actual]
            )
        for hold in status["holds"]:
            availability = hold["availability"]
            writer.writerow(
                [
                    "hold",
                    hold["kind"],
                    hold["label"],
                    f"capacity={availability.capacity}",
                    f"on_hold={availability.on_hold}",
                ]
            )
        for item in status["full"]:
            availability = item["availability"]
            writer.writerow(
                [
                    "full",
                    item["kind"],
                    item["label"],
                    f"capacity={availability.capacity}",
                    f"reserved={availability.reserved}, on_hold={availability.on_hold}",
                ]
            )
        return response


class AvailabilityHoldView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        model = AVAILABILITY_MODELS.get(kwargs["kind"])
        if model is None:
            raise ValidationError("Unknown availability type.")

        availability = get_object_or_404(model, pk=kwargs["pk"])
        try:
            on_hold = max(int(request.POST.get("on_hold", 0)), 0)
        except (TypeError, ValueError):
            messages.error(request, "Hold amount must be a non-negative number.")
            return redirect("enrollments:availability")

        availability.on_hold = min(on_hold, availability.capacity)
        availability.save(update_fields=["on_hold", "updated_at"])
        messages.success(request, "Availability hold updated.")
        return redirect("enrollments:availability")
