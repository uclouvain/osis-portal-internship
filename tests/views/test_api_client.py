##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import random
import uuid

from django.test import TestCase, override_settings
from osis_internship_sdk import DefaultApi, MasterGet, AllocationGet, PeriodGet, SpecialtyGet, OrganizationGet, \
    StudentAffectationGet, CohortGet, StudentGet, ScoreGet

from base.tests.factories.person import PersonFactory
from internship.models.enums.role_choice import ChoiceRole
from internship.views.api_client import InternshipAPIClient


class TestAPIClient(TestCase):

    @override_settings(URL_INTERNSHIP_API='test_url', OSIS_PORTAL_TOKEN='token')
    def test_new_internship_api_client(self):
        default_api = InternshipAPIClient()
        self.assertEqual(default_api.api_client.configuration.host, 'test_url')
        self.assertEqual(default_api.api_client.configuration.api_key['Authorization'], 'Token {}'.format('token'))


class MockAPI(DefaultApi):
    @classmethod
    def masters_get(*args, **kwargs):
        return {'count': 1, 'results': [MasterGet(role=ChoiceRole.MASTER.value).to_dict()]}

    @classmethod
    def masters_post(*args, **kwargs):
        return MasterGet(role=ChoiceRole.DELEGATE.value)

    @classmethod
    def masters_uuid_allocations_get(*args, **kwargs):
        return {'count': 1, 'results': [AllocationGet(
            organization={'uuid': uuid.uuid4(), 'reference': '00'},
            specialty={'uuid': uuid.uuid4(), 'acronym': 'TEST'}
        ).to_dict()]}

    @classmethod
    def periods_get(*args, **kwargs):
        return {'count': 1, 'results': [PeriodGet().to_dict()]}

    @classmethod
    def specialties_uuid_get(*args, **kwargs):
        return SpecialtyGet(uuid=uuid.uuid4(), cohort=CohortGet())

    @classmethod
    def organizations_uuid_get(*args, **kwargs):
        return OrganizationGet(uuid=uuid.uuid4()).to_dict()

    @classmethod
    def students_affectations_specialty_organization_get(*args, **kwargs):
        affectation = StudentAffectationGet(student={'uuid': uuid.uuid4()}, period={'uuid': uuid.uuid4()}).to_dict()
        affectation['uuid'] = uuid.uuid4()
        return {'count': 1, 'results': [affectation], 'next': 'next_url', 'previous': 'previous_url'}

    @classmethod
    def students_affectations_uuid_get(*args, **kwargs):
        student = StudentGet(person=PersonFactory())
        student.__setattr__('uuid', uuid.uuid4())
        return StudentAffectationGet(student=student, period=PeriodGet())

    @classmethod
    def scores_student_uuid_period_uuid_get(*args, **kwargs):
        return ScoreGet(objectives={}, comments={})

    @classmethod
    def scores_student_uuid_period_uuid_put(*args, **kwargs):
        return kwargs.get('score_get')

    @classmethod
    def masters_allocations_specialty_organization_get(*args, **kwargs):
        return {'count': 1, 'results': [AllocationGet(uuid=uuid.uuid4()).to_dict()]}

    @classmethod
    def masters_allocations_specialty_organization_post(*args, **kwargs):
        return AllocationGet(uuid=uuid.uuid4())

    @classmethod
    def masters_allocations_uuid_delete(*args, **kwargs):
        return AllocationGet(uuid=uuid.uuid4())

    @classmethod
    def scores_affectation_uuid_validate_get_with_http_info(*args, **kwargs):
        success_response = None, 200, {}
        error_response = {'error': 'error'}, 404, {}
        return random.choice([success_response, error_response])
