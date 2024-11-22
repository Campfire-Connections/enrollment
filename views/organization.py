# enrollment/views/organization.py

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from ..models.organization import OrganizationEnrollment, OrganizationCourse
from django.urls import reverse_lazy


class OrganizationEnrollmentIndexView(ListView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/index.html"
    context_object_name = "organization_enrollments"


class OrganizationEnrollmentShowView(DetailView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/show.html"
    context_object_name = "organization_enrollment"


class OrganizationEnrollmentCreateView(CreateView):
    model = OrganizationEnrollment
    fields = ["name", "start", "end", "organization"]
    template_name = "organization_enrollment/form.html"
    success_url = reverse_lazy("organization_enrollment:index")


class OrganizationEnrollmentUpdateView(UpdateView):
    model = OrganizationEnrollment
    fields = ["name", "start", "end", "organization"]
    template_name = "organization_enrollment/form.html"
    success_url = reverse_lazy("organization_enrollment:index")


class OrganizationEnrollmentDeleteView(DeleteView):
    model = OrganizationEnrollment
    template_name = "organization_enrollment/confirm_delete.html"
    success_url = reverse_lazy("organization_enrollment:index")


# Similar views for OrganizationCourse
class OrganizationCourseIndexView(ListView):
    model = OrganizationCourse
    template_name = "organization_course/index.html"
    context_object_name = "organization_courses"


class OrganizationCourseShowView(DetailView):
    model = OrganizationCourse
    template_name = "organization_course/show.html"
    context_object_name = "organization_course"


class OrganizationCourseCreateView(CreateView):
    model = OrganizationCourse
    fields = ["name", "course", "organization_enrollment"]
    template_name = "organization_course/form.html"
    success_url = reverse_lazy("organization_course:index")


class OrganizationCourseUpdateView(UpdateView):
    model = OrganizationCourse
    fields = ["name", "course", "organization_enrollment"]
    template_name = "organization_course/form.html"
    success_url = reverse_lazy("organization_course:index")


class OrganizationCourseDeleteView(DeleteView):
    model = OrganizationCourse
    template_name = "organization_course/confirm_delete.html"
    success_url = reverse_lazy("organization_course:index")
