# enrollment/mixins/active_enrollment.py

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
