# enrollment/views/facility_class.py

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from course.models.facility_class import FacilityClass
from ..models.facility import FacilityEnrollment
from ..forms.facility_class import FacilityClassForm


class ManageView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "facility_class/manage.html"

    def test_func(self):
        # Ensure the user is a faculty admin
        return self.request.user.user_type == "FACULTY" and self.request.user.is_admin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the facility the faculty admin belongs to
        faculty_profile = self.request.user.facultyprofile
        facility = faculty_profile.facility

        # Fetch facility enrollment and facility classes
        facility_enrollment = FacilityEnrollment.objects.filter(facility=facility)
        facility_classes = FacilityClass.objects.filter(
            facility_enrollment__facility=facility
        )

        context["facility"] = facility
        context["facility_enrollment"] = facility_enrollment
        context["facility_classes"] = facility_classes
        context["facility_class_form"] = FacilityClassForm()

        return context

    def post(self, request, *args, **kwargs):
        # Handle form submissions for creating or editing classes
        facility_class_id = request.POST.get("facility_class_id")
        facility_class_form = FacilityClassForm(request.POST)

        if facility_class_id:
            facility_class = get_object_or_404(FacilityClass, id=facility_class_id)
            if "edit_facility_class" in request.POST:
                # Edit existing class
                facility_class_form = FacilityClassForm(
                    request.POST, instance=facility_class
                )
                if facility_class_form.is_valid():
                    facility_class_form.save()
                    return redirect(reverse_lazy("facility_class_manage"))
            elif "delete_facility_class" in request.POST:
                # Delete existing class
                facility_class.delete()
                return redirect(reverse_lazy("facility_class_manage"))

        elif "add_facility_class" in request.POST and facility_class_form.is_valid():
            # Add a new facility class
            facility_class_form.save()
            return redirect(reverse_lazy("facility_class_manage"))

        return super().post(request, *args, **kwargs)
