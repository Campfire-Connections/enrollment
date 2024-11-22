# enrollment/views/facility.py

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django_tables2 import MultiTableMixin, SingleTableView
from django_tables2.config import RequestConfig
from ..models.facility import (
    FacilityEnrollment,
    FacilityClassEnrollment,
    FacultyEnrollment,
    FacultyClassEnrollment,
)
from ..models.temporal import Week
from ..tables.temporal import WeekTable, PeriodTable
from facility.models.facility import Facility

class ManageView(
    LoginRequiredMixin, UserPassesTestMixin, MultiTableMixin, TemplateView
):
    template_name = "facility/manage.html"
    enrollment = None
    facility = None
    def get_tables(self):
        enrollment = self.get_enrollment()

        # Construct querystrings
        weeks_qs = Week.objects.filter(facility_enrollment=enrollment)

        # Build tables with querystrings
        week_table = WeekTable(weeks_qs)

        # Configure tables with pagination and sorting
        RequestConfig(self.request, paginate={"per_page": 8}).configure(
            week_table
        )

        return [
            week_table,
        ]

    def get_context_data(self, **kwargs):
        """
        Constructs and returns the context data for rendering a template, including various tables 
        and related entities for a specific facility. This function enhances the context with 
        additional information and other related data.

        Args:
            self: The instance of the class.
            **kwargs: Additional keyword arguments.

        Returns:
            dict: A dictionary containing the context data for the template, including tables with 
                names and various related entities.
        """

        context = super().get_context_data(**kwargs)
        facility = self.get_facility()
        enrollment = self.get_enrollment()

        tables_with_names = [
            {
                "table": table,
                "name": table.Meta.model._meta.verbose_name_plural,
                "create_url": table.get_url(
                    "add", context={"facility_slug": facility.slug, "facility_enrollment_slug": enrollment.slug}
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
            }
        )

        return context

    def get_facility(self):
        if self.facility is None:
            facility_slug = self.kwargs.get('facility_slug')
            self.facility = get_object_or_404(Facility, slug=facility_slug)
        return self.facility

    def get_enrollment(self):
        if self.enrollment is None:
            enrollment_slug = self.kwargs.get('facility_enrollment_slug')
            self.enrollment = get_object_or_404(FacilityEnrollment, slug=enrollment_slug)
        return self.enrollment

    def test_func(self):
        # Check if the user is a faculty member with admin privileges
        return self.request.user.user_type == "FACULTY" and self.request.user.is_admin


class FacilityEnrollmentIndexView(ListView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/index.html"
    context_object_name = "facility_enrollments"


class FacilityEnrollmentShowView(DetailView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/show.html"
    context_object_name = "facility_enrollment"


class FacilityEnrollmentCreateView(CreateView):
    model = FacilityEnrollment
    fields = "__all__"
    template_name = "facility-enrollment/form.html"
    success_url = reverse_lazy("facility:facility_enrollment_index")


class FacilityEnrollmentUpdateView(UpdateView):
    model = FacilityEnrollment
    fields = "__all__"
    template_name = "facility-enrollment/form.html"
    success_url = reverse_lazy("facility:facility_enrollment_index")


class FacilityEnrollmentDeleteView(DeleteView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/confirm_delete.html"
    success_url = reverse_lazy("facility:facility_enrollment_index")


class FacilityClassEnrollmentIndexView(ListView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/index.html"
    context_object_name = "facility_class_enrollments"


class FacilityClassEnrollmentShowView(DetailView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/show.html"
    context_object_name = "facility_class_enrollment"


class FacilityClassEnrollmentCreateView(CreateView):
    model = FacilityClassEnrollment
    fields = "__all__"
    template_name = "facility-class-enrollment/form.html"
    success_url = reverse_lazy("facility:facility_class_enrollment_index")


class FacilityClassEnrollmentUpdateView(UpdateView):
    model = FacilityClassEnrollment
    fields = "__all__"
    template_name = "facility-class-enrollment/form.html"
    success_url = reverse_lazy("facility:facility_class_enrollment_index")


class FacilityClassEnrollmentDeleteView(DeleteView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("facility:facility_class_enrollment_index")


class FacultyEnrollmentIndexView(ListView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/index.html"
    context_object_name = "faculty_enrollments"


class FacultyEnrollmentShowView(DetailView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/show.html"
    context_object_name = "faculty_enrollment"


class FacultyEnrollmentCreateView(CreateView):
    model = FacultyEnrollment
    fields = "__all__"
    template_name = "faculty-enrollment/form.html"
    success_url = reverse_lazy("facility:faculty_enrollment_index")


class FacultyEnrollmentUpdateView(UpdateView):
    model = FacultyEnrollment
    fields = "__all__"
    template_name = "faculty-enrollment/form.html"
    success_url = reverse_lazy("facility:faculty_enrollment_index")


class FacultyEnrollmentDeleteView(DeleteView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/confirm_delete.html"
    success_url = reverse_lazy("facility:faculty_enrollment_index")


class FacultyClassEnrollmentIndexView(ListView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/index.html"
    context_object_name = "faculty_class_enrollments"


class FacultyClassEnrollmentShowView(DetailView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/show.html"
    context_object_name = "faculty_class_enrollment"


class FacultyClassEnrollmentCreateView(CreateView):
    model = FacultyClassEnrollment
    fields = "__all__"
    template_name = "faculty-class-enrollment/form.html"
    success_url = reverse_lazy("facility:faculty_class_enrollment_index")


class FacultyClassEnrollmentUpdateView(UpdateView):
    model = FacultyClassEnrollment
    fields = "__all__"
    template_name = "faculty-class-enrollment/form.html"
    success_url = reverse_lazy("facility:faculty_class_enrollment_index")


class FacultyClassEnrollmentDeleteView(DeleteView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/confirm_delete.html"
    success_url = reverse_lazy("facility:faculty_class_enrollment_index")
