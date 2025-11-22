# enrollment/views/facility.py

from django.urls import reverse
from django.shortcuts import get_object_or_404

from core.views.base import (
    BaseManageView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseTableListView,
    BaseUpdateView,
)
from facility.models.facility import Facility
from facility.tables.faculty import FacultyTable
from facility.models.faculty import FacultyProfile

from ..models.facility import FacilityEnrollment
from ..models.faculty import FacultyEnrollment
from ..models.facility_class import FacilityClassEnrollment as FacilityClassEnrollmentRecord
from ..models.faculty_class import FacultyClassEnrollment as FacultyClassAssignment
from ..forms.facility import FacilityEnrollmentForm
from ..forms.facility_class import FacilityClassEnrollmentForm
from ..forms.faculty import FacultyEnrollmentForm
from ..forms.faculty_class import FacultyClassEnrollmentForm as FacultyClassAssignmentForm
from ..models.temporal import Week
from ..tables.week import WeekTable
from ..tables.facility import FacilityEnrollmentTable
from ..tables.facility_class import FacilityClassEnrollmentTable
from ..tables.faculty import FacultyEnrollmentTable
from ..tables.faculty_class import FacultyClassEnrollmentTable as FacultyClassAssignmentTable
from ..services import SchedulingService
from ..mixin import SchedulingServiceFormMixin


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
            "faculty": {
                "class": FacultyTable,
                "queryset": FacultyProfile.objects.filter(
                    faculty_enrollments__facility_enrollment=enrollment,
                )
                .select_related("user")
                #.prefetch_related("facultyenrollment_set"),
                # "queryset": User.faculty_manager.for_facility_enrollment(enrollment),
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
                FacilityEnrollment.objects.with_schedule(), slug=enrollment_slug
            )

        return self.enrollment

    def __init__(self):
        self.enrollment = None
        self.facility = None


class FacilityEnrollmentIndexView(BaseTableListView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/list.html"
    context_object_name = "facility enrollments"
    table_class = FacilityEnrollmentTable

    def get_queryset(self):
        return FacilityEnrollment.objects.with_schedule()


class FacilityEnrollmentShowView(BaseDetailView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/show.html"
    context_object_name = "facility enrollment"
    slug_field = "slug"
    slug_url_kwarg = "facility_enrollment_slug"

    def get_queryset(self):
        return FacilityEnrollment.objects.with_schedule()

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

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={"facility_slug": self.kwargs.get("facility_slug")},
        )


class FacilityEnrollmentUpdateView(BaseUpdateView):
    model = FacilityEnrollment
    form_class = FacilityEnrollmentForm
    template_name = "facility-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={"facility_slug": self.kwargs.get("facility_slug")},
        )


class FacilityEnrollmentDeleteView(BaseDeleteView):
    model = FacilityEnrollment
    template_name = "facility-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:enrollments:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={"facility_slug": self.kwargs.get("facility_slug")},
        )


class FacilityClassEnrollmentIndexView(BaseTableListView):
    model = FacilityClassEnrollmentRecord
    template_name = "facility-class-enrollment/list.html"
    context_object_name = "facility class enrollments"
    table_class = FacilityClassEnrollmentTable


class FacilityClassEnrollmentShowView(BaseDetailView):
    model = FacilityClassEnrollmentRecord
    template_name = "facility-class-enrollment/show.html"
    context_object_name = "facility class enrollment"
    slug_field = "slug"
    slug_url_kwarg = "facility_class_enrollment_slug"


class FacilityClassEnrollmentCreateView(BaseCreateView):
    model = FacilityClassEnrollmentRecord
    form_class = FacilityClassEnrollmentForm
    template_name = "facility-class-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "facility_enrollment_slug": self.kwargs.get("facility_enrollment_slug"),
            },
        )


class FacilityClassEnrollmentUpdateView(BaseUpdateView):
    model = FacilityClassEnrollmentRecord
    form_class = FacilityClassEnrollmentForm
    template_name = "facility-class-enrollment/form.html"
    success_url_pattern = "facilities:enrollments:classes:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "facility_enrollment_slug": self.kwargs.get("facility_enrollment_slug"),
            },
        )


class FacilityClassEnrollmentDeleteView(BaseDeleteView):
    model = FacilityClassEnrollmentRecord
    template_name = "facility-class-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:enrollments:classes:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "facility_enrollment_slug": self.kwargs.get("facility_enrollment_slug"),
            },
        )


# Faculty Enrollment


class FacultyEnrollmentIndexView(BaseTableListView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/list.html"
    context_object_name = "faculty enrollments"
    table_class = FacultyEnrollmentTable


class FacultyEnrollmentShowView(BaseDetailView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/show.html"
    context_object_name = "faculty enrollment"
    slug_field = "slug"
    slug_url_kwarg = "faculty_enrollment_slug"


class FacultyEnrollmentCreateView(SchedulingServiceFormMixin, BaseCreateView):
    model = FacultyEnrollment
    form_class = FacultyEnrollmentForm
    template_name = "faculty-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:index"
    service_class = SchedulingService
    service_method = "schedule_faculty_enrollment"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
            },
        )

    def get_service_kwargs(self, form):
        return {
            "faculty": form.cleaned_data["faculty"],
            "facility_enrollment": form.cleaned_data["facility_enrollment"],
            "quarters": form.cleaned_data["quarters"],
            "role": form.cleaned_data.get("role"),
        }


class FacultyEnrollmentUpdateView(SchedulingServiceFormMixin, BaseUpdateView):
    model = FacultyEnrollment
    form_class = FacultyEnrollmentForm
    template_name = "faculty-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:index"
    service_class = SchedulingService
    service_method = "schedule_faculty_enrollment"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
            },
        )

    def form_valid(self, form):
        self.object = self.get_object()
        return super().form_valid(form)

    def get_service_kwargs(self, form):
        return {
            "faculty": form.cleaned_data["faculty"],
            "facility_enrollment": form.cleaned_data["facility_enrollment"],
            "quarters": form.cleaned_data["quarters"],
            "role": form.cleaned_data.get("role"),
            "instance": self.object,
        }

class FacultyEnrollmentDeleteView(BaseDeleteView):
    model = FacultyEnrollment
    template_name = "faculty-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:faculty:enrollments:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
            },
        )


# Faculty Class Enrollment


class FacultyClassEnrollmentIndexView(BaseTableListView):
    model = FacultyClassAssignment
    template_name = "faculty-class-enrollment/list.html"
    context_object_name = "faculty class enrollments"
    table_class = FacultyClassAssignmentTable


class FacultyClassEnrollmentShowView(BaseDetailView):
    model = FacultyClassAssignment
    template_name = "faculty-class-enrollment/show.html"
    context_object_name = "faculty class enrollment"
    slug_field = "slug"
    slug_url_kwarg = "faculty_class_enrollment_slug"


class FacultyClassEnrollmentCreateView(BaseCreateView):
    model = FacultyClassAssignment
    form_class = FacultyClassAssignmentForm
    template_name = "faculty-class-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:show"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
                "faculty_enrollment_slug": self.kwargs.get("faculty_enrollment_slug"),
                "faculty_class_enrollment_slug": self.get_object(),
            },
        )


class FacultyClassEnrollmentUpdateView(BaseUpdateView):
    model = FacultyClassAssignment
    form_class = FacultyClassAssignmentForm
    template_name = "faculty-class-enrollment/form.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:show"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
                "faculty_enrollment_slug": self.kwargs.get("faculty_enrollment_slug"),
                "faculty_class_enrollment_slug": self.get_object(),
            },
        )


class FacultyClassEnrollmentDeleteView(BaseDeleteView):
    model = FacultyClassAssignment
    template_name = "faculty-class-enrollment/confirm_delete.html"
    success_url_pattern = "facilities:faculty:enrollments:classes:index"

    def get_success_url(self):
        """
        Dynamically generate the success URL using the facility_slug from kwargs.
        """
        return reverse(
            self.success_url_pattern,
            kwargs={
                "facility_slug": self.kwargs.get("facility_slug"),
                "faculty_slug": self.kwargs.get("faculty_slug"),
                "faculty_enrollment_slug": self.kwargs.get("faculty_enrollment_slug"),
            },
        )
