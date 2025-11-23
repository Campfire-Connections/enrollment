# enrollment/forms/attendee.py

from django import forms

class AttendeeQuartersAssignmentForm(forms.Form):
    """
    Placeholder: Assign an attendee to a quarters/housing unit.
    """
    quarters = forms.CharField(required=True)


class AttendeeClassAssignmentForm(forms.Form):
    """
    Placeholder: Attendee joins a class.
    """
    class_id = forms.CharField(required=True)
    