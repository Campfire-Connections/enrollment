# enrollment/views/facility_class.py

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy

from core.views.base import BaseManageView
from core.mixins.views import LoginRequiredMixin, UserPassesTestMixin
from core.utils import is_faculty_admin

from course.models.facility_class import FacilityClass
from ..models.facility import FacilityEnrollment
from ..forms.facility_class import FacilityClassForm


class ManageView(LoginRequiredMixin, UserPassesTestMixin, BaseManageView):
    """
    Manage facility classes for the current faculty-admin's facility.
    """

    template_name = "facility_class/manage.html"

    def test_func(self):
        # Ensure the user is a faculty admin
        return is_faculty_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        faculty_profile = getattr(self.request.user, "facultyprofile", None)
        facility = getattr(faculty_profile, "facility", None)

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
        facility_class_id = request.POST.get("facility_class_id")
        facility_class_form = FacilityClassForm(request.POST)

        if facility_class_id:
            facility_class = get_object_or_404(FacilityClass, id=facility_class_id)
            if "edit_facility_class" in request.POST:
                facility_class_form = FacilityClassForm(
                    request.POST, instance=facility_class
                )
                if facility_class_form.is_valid():
                    facility_class_form.save()
                    return redirect(reverse_lazy("facility_class_manage"))
            elif "delete_facility_class" in request.POST:
                facility_class.delete()
                return redirect(reverse_lazy("facility_class_manage"))

        elif "add_facility_class" in request.POST and facility_class_form.is_valid():
            facility_class_form.save()
            return redirect(reverse_lazy("facility_class_manage"))

        return super().post(request, *args, **kwargs)
