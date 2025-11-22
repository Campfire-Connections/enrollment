# enrollment/mixin.py

from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from enrollment.services import SchedulingService
from enrollment.utils import format_validation_error


class ActiveEnrollmentMixin:
    """Handles active enrollment for users."""

    def get_active_enrollment(self, user):
        """Return the active enrollment."""
        return user.active_enrollment

    def set_active_enrollment(self, user, enrollment):
        """Set an active enrollment for the user."""
        if enrollment in user.enrollments.all():
            user.active_enrollment = enrollment
            user.save()
        else:
            raise ValueError("User is not enrolled in this session.")


class SchedulingServiceFormMixin:
    """
    Shared form mixin that routes create/update actions through the
    scheduling service so capacity validations remain consistent.
    """

    service_class = SchedulingService
    service_method = None

    def get_service_method(self):
        if not self.service_method:
            raise NotImplementedError("service_method must be set.")
        return self.service_method

    def get_service_kwargs(self, form):
        return form.cleaned_data

    def call_service(self, form):
        service = self.service_class(user=getattr(self.request, "user", None))
        method = getattr(service, self.get_service_method())
        return method(**self.get_service_kwargs(form))

    def form_valid(self, form):
        try:
            self.object = self.call_service(form)
        except ValidationError as exc:
            form.add_error(None, format_validation_error(exc))
            return self.form_invalid(form)
        return HttpResponseRedirect(self.get_success_url())
