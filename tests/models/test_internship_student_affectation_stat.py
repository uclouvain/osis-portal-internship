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
import datetime

from django.test import TestCase

from base.tests.models import test_student
from internship.models import internship_student_affectation_stat as mdl_student_affectation
from internship.models import period as mdl_period
from internship.tests.factories.cohort import CohortFactory
from internship.tests.models import test_organization, test_internship_speciality


def create_period(name="P1", start=datetime.date(2010, 1, 1), end=datetime.date(2010, 1, 20), cohort=None):
    if cohort is None:
        cohort = CohortFactory()
    period = mdl_period.Period(name=name, date_start=start, date_end=end, cohort=cohort)
    period.save()
    return period


def create_internship_student_affectation_stat(student):
    organization = test_organization.create_organization()
    speciality = test_internship_speciality.create_speciality()
    period = create_period()

    student_affectation = mdl_student_affectation.InternshipStudentAffectationStat(student=student, period=period,
                                                                                   organization=organization,
                                                                                   speciality=speciality,
                                                                                   cost=10)
    student_affectation.save()
    return student_affectation


class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = test_student.create_student("64641200")
        cls.other_student = test_student.create_student("60601200")

    def test_with_no_match(self):
        create_internship_student_affectation_stat(self.other_student)
        student_affectations = list(mdl_student_affectation.search(student=self.student))
        self.assertFalse(student_affectations)

    def test_with_match(self):
        expected = create_internship_student_affectation_stat(self.student)
        actual = list(mdl_student_affectation.search(student=self.student))
        self.assertEqual([expected], actual)
