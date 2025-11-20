from core.tests import BaseDomainTestCase


class OrganizationEnrollmentTests(BaseDomainTestCase):
    def test_get_courses_returns_related_instances(self):
        courses = self.org_enrollment.get_courses()
        self.assertIn(self.org_course, courses)
