##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import User
from django.test import TestCase

from base.models import person as mdl_person
from base.tests.factories.user import UserFactory
from base.tests.models import test_person
from internship.models import internship_student_information as mdl_student_information
from internship.tests.factories.cohort import CohortFactory


def create_student_information(user, cohort=None, person=None):
    if person is None:
        person = test_person.create_person_with_user(user)

    if cohort is None:
        cohort = CohortFactory()
    student_information = mdl_student_information.InternshipStudentInformation(person=person, location="location",
                                                                               cohort=cohort,
                                                                               postal_code="00", city="city",
                                                                               country="country")
    student_information.save()
    return student_information


class TestFindByUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory()
        cls.user = User.objects.create_user('user', 'user@test.com', 'userpass')

    def test_with_no_data(self):
        student_information = mdl_student_information.find_by_user_in_cohort(self.user, self.cohort)
        self.assertFalse(student_information)

    def test_with_no_information_for_user(self):
        other_user = User.objects.create_user('other_user', 'other_user@test.com', 'userpass')
        create_student_information(other_user, cohort=self.cohort)

        student_information = mdl_student_information.find_by_user_in_cohort(self.user, self.cohort)
        self.assertFalse(student_information)

    def test_with_information_for_user(self):
        expected = create_student_information(self.user, cohort=self.cohort)
        actual = mdl_student_information.find_by_user_in_cohort(self.user, cohort=self.cohort)

        self.assertEqual(expected, actual)


class TestFindByPerson(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.student_information = create_student_information(cls.user)

    def test_with_no_information_for_user(self):
        other_person = test_person.create_person("other", "another")

        student_information = mdl_student_information.find_by_person(other_person)
        self.assertFalse(student_information)

    def test_with_information_for_user(self):
        self.assertEqual(mdl_student_information.find_by_person(self.student_information.person).first(),
                         self.student_information)


class TestExistsByPerson(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.student_information = create_student_information(cls.user)
        person = mdl_person.find_by_user(cls.user)
        cls.student_information2 = create_student_information(cls.user, person=person)

    def test_with_no_information_for_user(self):
        other_person = test_person.create_person("other", "another")
        student_information_exists = mdl_student_information.exists_by_person(other_person)
        self.assertFalse(student_information_exists)

    def test_with_information_for_user(self):
        student_information_exists = mdl_student_information.exists_by_person(self.student_information.person)
        self.assertTrue(student_information_exists)
