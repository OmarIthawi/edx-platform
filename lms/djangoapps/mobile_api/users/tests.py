"""
Tests for users API
"""
from rest_framework.test import APITestCase
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from courseware.tests.factories import UserFactory
from django.core.urlresolvers import reverse
from mobile_api.users.serializers import CourseEnrollmentSerializer
from student.models import CourseEnrollment
from student import auth


class TestUserApi(ModuleStoreTestCase, APITestCase):
    """
    Test the user info API
    """
    def setUp(self):
        super(TestUserApi, self).setUp()
        self.course = CourseFactory.create(mobile_available=True)
        self.user = UserFactory.create()
        self.password = 'test'
        self.username = self.user.username

    def tearDown(self):
        super(TestUserApi, self).tearDown()
        self.client.logout()

    def _enrollmentURL(self):
        return reverse('courseenrollment-detail', kwargs={'username': self.user.username})

    def _enroll(self, course):
        """
        enroll test user in test course
        """
        resp = self.client.post(reverse('change_enrollment'), {
            'enrollment_action': 'enroll',
            'course_id': course.id.to_deprecated_string(),
            'check_access': True,
        })
        self.assertEqual(resp.status_code, 200)

    def _verify_single_course(self, courses, expected_course):
        """
        check that courses matches expected_course
        """
        self.assertEqual(len(courses), 1)
        course = courses[0]['course']
        self.assertTrue('video_outline' in course)
        self.assertTrue('course_handouts' in course)
        self.assertEqual(course['id'], expected_course.id.to_deprecated_string())
        self.assertEqual(courses[0]['mode'], 'honor')

    def test_beta_enrollments(self):
        self._test_privileged_enrollments(auth.CourseBetaTesterRole)

    def test_staff_enrollments(self):
        self._test_privileged_enrollments(auth.CourseStaffRole)

    def test_instructor_enrollments(self):
        self._test_privileged_enrollments(auth.CourseInstructorRole)

    def _test_privileged_enrollments(self, role):
        url = self._enrollmentURL()
        non_mobile_course = CourseFactory.create(mobile_available=False)
        self.client.login(username=self.username, password=self.password)

        self._enroll(non_mobile_course)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, []) # pylint: disable=E1103

        role(non_mobile_course.id).add_users(self.user)

        response = self.client.get(url)
        courses = response.data # pylint: disable=E1103
        self._verify_single_course(courses, non_mobile_course)

    def test_mobile_enrollments(self):
        url = self._enrollmentURL()

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])  # pylint: disable=E1103

        self._enroll(self.course)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        courses = response.data  # pylint: disable=E1103

        self._verify_single_course(courses, self.course)

    def test_user_overview(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse('user-detail', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data  # pylint: disable=E1103
        self.assertEqual(data['username'], self.user.username)
        self.assertEqual(data['email'], self.user.email)

    def test_overview_anon(self):
        # anonymous disallowed
        url = reverse('user-detail', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        # can't get info on someone else
        other = UserFactory.create()
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('user-detail', kwargs={'username': other.username}))
        self.assertEqual(response.status_code, 403)

    def test_redirect_userinfo(self):
        url = '/api/mobile/v0.5/my_user_info'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.username in response['location'])

    def test_course_serializer(self):
        self.client.login(username=self.username, password=self.password)
        self._enroll(self.course)
        serialized = CourseEnrollmentSerializer(CourseEnrollment.enrollments_for_user(self.user)[0]).data  # pylint: disable=E1101
        self.assertEqual(serialized['course']['video_outline'], None)
        self.assertEqual(serialized['course']['name'], self.course.display_name)
