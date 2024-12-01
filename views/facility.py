# enrollment/views/facility.py

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404

from core.views.base import (
    BaseManageView,
    BaseIndexByFilterTableView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseTableListView,
    BaseUpdateView,
)
from facility.models.facility import Facility

from ..models.facility import (
    FacilityEnrollment,
    FacilityClassEnrollment,
    FacultyEnrollment,
    FacultyClassEnrollment,
)
from ..forms.facility import FacilityEnrollmentForm, FacilityClassEnrollmentForm, 
from ..forms.faculty_class import FacultyClassEnrollmentForm
from ..models.temporal import Week
from ..tables.temporal import WeekTable
from ..tables.facility import FacilityEnrollmentTable, FacilityClassEnrollmentTable, FacultyEnrollmentTable, FacultyClassEnrollmentTable

class FacilityEnrollmentManageView(BaseManageView):
    template_name = "facility/manage.html"

    def get_tables_config(self):
        enrollment = self.get_enrollment()
        return {
            "weeks": {
                "class": WeekTable,
                "queryset": Week.objects.filter(facility_enrollment=enrollment),
                "paginate_by": 7,
            },
        }

    def test_func(self):
        """
        Check if the user is a faculty member with admin privileges.
        """
        return self.request.user.user_type == "FACULTY" and self.request.user.is_admin

    def get_create_url(self, table):
        facility = self.get_facility()
        enrollment = self.get_enrollment()
        return table.get_url(
            "add",
            context={
                "facility_slug": facility.slug,
                "facility_enrollment_slug": enrollment.slug,
            },
        )

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


class FacilityEnrollmentIndexView(BaseTableListView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/index.html"
    context_object_name = "facility enrollments"
    table_class = FacilityEnrollmentTable


class FacilityEnrollmentShowView(BaseDetailView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/show.html"
    context_object_name = "facility enrollment"
    slug_field = "slug"
    slug_url_kwarg = "facility_enrollment_slug"

    def get_tables_config(self):
        enrollment = self.get_object()
        return {
            "weeks_table": {
                "class": WeekTable,
                "queryset": Week.objects.filter(facility_enrollment=enrollment),
            },
        }

class FacilityEnrollmentCreateView(BaseCreateView):
    model = FacilityEnrollment
    form_class = FacilityEnrollmentForm
    template_name = "facility-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
    }


class FacilityEnrollmentUpdateView(BaseUpdateView):
    model = FacilityEnrollment
    form_class = FacilityEnrollmentForm
    template_name = "facility-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
    }


class FacilityEnrollmentDeleteView(BaseDeleteView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
    }


class FacilityClassEnrollmentIndexView(BaseTableListView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/index.html"
    context_object_name = "facility class enrollments"
    table_class = FacilityClassEnrollmentTable


class FacilityClassEnrollmentShowView(BaseDetailView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/show.html"
    context_object_name = "facility class enrollment"
    slug_field = "slug"
    slug_url_kwarg = "facility_class_enrollment_slug"


class FacilityClassEnrollmentCreateView(BaseCreateView):
    model = FacilityClassEnrollment
    form_class = FacilityClassEnrollmentForm
    template_name = "facility-class-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "facility_enrollment_slug": self.kwargs.get('facility_enrollment_slug'),
    }


class FacilityClassEnrollmentUpdateView(BaseUpdateView):
    model = FacilityClassEnrollment
    form_class = FacilityClassEnrollmentForm
    template_name = "facility-class-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:classes:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "facility_enrollment_slug": self.kwargs.get('facility_enrollment_slug'),
    }

class FacilityClassEnrollmentDeleteView(BaseDeleteView):
    model = FacilityClassEnrollment
    template_name = "facility-class-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:enrollments:classes:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "facility_enrollment_slug": self.kwargs.get('facility_enrollment_slug'),
    }

# Faculty Enrollment

class FacultyEnrollmentIndexView(BaseTableListView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/index.html"
    context_object_name = "faculty enrollments"
    table_class = FacultyEnrollmentTable


class FacultyEnrollmentShowView(BaseDetailView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/show.html"
    context_object_name = "faculty enrollment"
    slug_field = "slug"
    slug_url_kwarg = "faculty_enrollment_slug"


class FacultyEnrollmentCreateView(BaseCreateView):
    model = FacultyEnrollment
    form_class = FacultyEnrollmentForm
    template_name = "faculty-enrollment/form.html"
        success_url_pattern = "facilities:faculty:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
    }


class FacultyEnrollmentUpdateView(BaseUpdateView):
    model = FacultyEnrollment
    form_class = FacultyEnrollmentForm
    template_name = "faculty-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
    }

class FacultyEnrollmentDeleteView(BaseDeleteView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:faculty:enrollments:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
    }

# Faculty Class Enrollment

class FacultyClassEnrollmentIndexView(BaseTableListView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/index.html"
    context_object_name = "faculty class enrollments"
    table_class = FacultyClassEnrollmentTable


class FacultyClassEnrollmentShowView(BaseDetailView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/show.html"
    context_object_name = "faculty class enrollment"
    slug_field = "slug"
    slug_url_kwarg = "faculty_class_enrollment_slug"


class FacultyClassEnrollmentCreateView(BaseCreateView):
    model = FacultyClassEnrollment
    form_class = FacultyClassEnrollmentForm
    template_name = "faculty-class-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:show"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
        "faculty_enrollment_slug": self.kwargs.get('faculty_enrollment_slug'),
        "faculty_class_enrollment_slug": self.get_object(),
    }


class FacultyClassEnrollmentUpdateView(BaseUpdateView):
    model = FacultyClassEnrollment
    form_class = FacultyClassEnrollmentForm
    template_name = "faculty-class-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:show"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
        "faculty_enrollment_slug": self.kwargs.get('faculty_enrollment_slug'),
        "faculty_class_enrollment_slug": self.get_object(),
    }

class FacultyClassEnrollmentDeleteView(BaseDeleteView):
    model = FacultyClassEnrollment
    template_name = "faculty-class-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:index"
    success_url_params = {
        "facility_slug": self.kwargs.get('facility_slug'),
        "faculty_slug": self.kwargs.get('faculty_slug'),
        "faculty_enrollment_slug": self.kwargs.get('faculty_enrollment_slug'),
    }
