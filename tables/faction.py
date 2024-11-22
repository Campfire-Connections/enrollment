# enrollment/tables/faction.py

import django_tables2 as tables
from pages.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.faction import FactionEnrollment


class FactionEnrollmentTable(ActionsColumnMixin, ActionUrlMixin,tables.Table):
    facility = tables.Column(accessor='week.facility_enrollment.facility', verbose_name="Facility")
    class Meta:
        model = FactionEnrollment
        faction = model.faction
        template_name = "django_tables2/bootstrap4.html"
        fields = ("facility", "quarters", "start", "end")
        attrs = {"class": "table table-striped table-bordered"}
    url_namespace = "factions:enrollments"
    urls = {
        'add': {
            'name': 'factions:enrollments:new',
            'kwargs': {'slug': 'faction__slug'},
        },
        'show': {
            'name': 'factions:enrollments:show',
            'kwargs': {'slug': 'faction__slug', 'enrollment_slug': 'slug'}
        },
        'edit': {
            'name': 'factions:enrollments:edit',
            'kwargs': {'slug': 'faction__slug', 'enrollment_slug': 'slug'}
        },
        'delete': {
            'name': 'factions:enrollments:delete',
            'kwargs': {'slug': 'faction__slug', 'enrollment_slug': 'slug'}
        },
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_actions_column()