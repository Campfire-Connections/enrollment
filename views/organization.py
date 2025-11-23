# enrollment/views/organization.py

from django.urls import reverse_lazy

from core.views.base import (
    BaseListView,
    BaseDetailView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
)

from ..models.organization import OrganizationEnrollment, OrganizationCourse


class OrganizationEnrollmentIndexView(BaseListView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/index.html"
    context_object_name = "organization_enrollments"


class OrganizationEnrollmentShowView(BaseDetailView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/show.html"
    context_object_name = "organization_enrollment"


class OrganizationEnrollmentCreateView(BaseCreateView):
    model = OrganizationEnrollment
    fields = ["name", "start", "end", "organization"]
    template_name = "organization_enrollment/form.html"
    success_url = reverse_lazy("organization_enrollment:index")


class OrganizationEnrollmentUpdateView(BaseUpdateView):
    model = OrganizationEnrollment
    fields = ["name", "start", "end", "organization"]
    template_name = "organization_enrollment/form.html"
    success_url = reverse_lazy("organization_enrollment:index")


class OrganizationEnrollmentDeleteView(BaseDeleteView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/confirm_delete.html"
    success_url = reverse_lazy("organization_enrollment:index")


class OrganizationCourseIndexView(BaseListView):
    model = OrganizationCourse
    template_name = "organization_course/index.html"
    context_object_name = "organization_courses"


class OrganizationCourseShowView(BaseDetailView):
    model = OrganizationCourse
    template_name = "organization_course/show.html"
    context_object_name = "organization_course"


class OrganizationCourseCreateView(BaseCreateView):
    model = OrganizationCourse
    fields = ["name", "course", "organization_enrollment"]
    template_name = "organization_course/form.html"
    success_url = reverse_lazy("organization_course:index")


class OrganizationCourseUpdateView(BaseUpdateView):
    model = OrganizationCourse
    fields = ["name", "course", "organization_enrollment"]
    template_name = "organization_course/form.html"
    success_url = reverse_lazy("organization_course:index")


class OrganizationCourseDeleteView(BaseDeleteView):
    model = OrganizationCourse
    template_name = "organization_course/confirm_delete.html"
    success_url = reverse_lazy("organization_course:index")
