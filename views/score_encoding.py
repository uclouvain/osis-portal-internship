############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
############################################################################

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk import ScoreGet

from base.views import layout
from internship.decorators.score_encoding_view_decorators import redirect_if_not_master
from internship.models.period import Period
from internship.models.score_encoding_utils import DEFAULT_PERIODS, APDS, COMMENTS_FIELDS, MIN_APDS, MAX_APDS, \
    AVAILABLE_GRADES
from internship.templatetags.selection_tags import only_number
from internship.views.api_client import get_master_by_email, get_master_allocations, get_active_period, get_specialty, \
    get_organization, get_score, get_affectation, update_score, \
    get_students_affectations_count, get_paginated_students_affectations, validate_internship_score


@login_required
@redirect_if_not_master
def view_score_encoding(request):
    master = get_master_by_email(request.user.email)
    allocations = get_master_allocations(master['uuid'])
    for allocation in allocations:
        allocation['total_amount'] = get_students_affectations_count(
            specialty_uuid=allocation['specialty']['uuid'],
            organization_uuid=allocation['organization']['uuid'],
        )
        allocation['amount_encoded'] = get_students_affectations_count(
            specialty_uuid=allocation['specialty']['uuid'],
            organization_uuid=allocation['organization']['uuid'],
            with_score=True
        )
    return layout.render(request, "internship_score_encoding.html", locals())


@login_required
@redirect_if_not_master
def view_score_encoding_sheet(request, specialty_uuid, organization_uuid):
    if request.GET.get('period'):
        selected_period = request.GET.get('period', "")
    else:
        active_period = get_active_period()
        selected_period = active_period['name'] if active_period else DEFAULT_PERIODS

    pagination_params = {'limit': request.GET.get('limit', '0'), 'offset': request.GET.get('offset', '0')}

    apds = APDS

    specialty = get_specialty(specialty_uuid)
    organization = get_organization(organization_uuid)

    students_affectations, previous, next, count = get_paginated_students_affectations(
        specialty_uuid, organization_uuid, selected_period, **pagination_params
    )

    periods = Period.objects.filter(cohort__name=specialty.cohort.name).order_by('date_start')

    for affectation in students_affectations:
        affectation['score'] = get_score(affectation['student']['uuid'], affectation['period']['uuid'])

    return layout.render(request, "internship_score_encoding_sheet.html", locals())


@login_required
@redirect_if_not_master
def view_score_encoding_form(request, specialty_uuid, organization_uuid, affectation_uuid):

    affectation = get_affectation(affectation_uuid)
    period = affectation.period
    student = affectation.student

    score = get_score(student.uuid, period.uuid)
    specialty = get_specialty(specialty_uuid)
    organization = get_organization(organization_uuid)

    apds = APDS
    comments_fields = COMMENTS_FIELDS
    available_grades = AVAILABLE_GRADES

    if request.POST:
        score = _build_score_to_update(request.POST, score)
        if not _validate_score(request.POST):
            _show_invalid_update_msg(request)
            return layout.render(request, "internship_score_encoding_form.html", locals())
        update = update_score(student.uuid, period.uuid, score)
        if update:
            _show_success_update_msg(request, period, student)
            return redirect(reverse('internship_score_encoding_sheet', kwargs={
                'specialty_uuid': specialty_uuid,
                'organization_uuid': organization_uuid,
            }))
        else:
            messages.add_message(request, messages.ERROR, _('An error occurred during score update'))

    return layout.render(request, "internship_score_encoding_form.html", locals())


@login_required
@redirect_if_not_master
def score_encoding_validate(request, affectation_uuid):
    data, status, headers = validate_internship_score(affectation_uuid)
    return JsonResponse({'success': status == 200, **data} if data else {'success': status == 200})


def _show_success_update_msg(request, period, student):
    messages.add_message(
        request,
        messages.SUCCESS,
        _("Score updated successfully for {}'s internship during {}".format(
            student.person.last_name, period.name
        ))
    )


def _show_invalid_update_msg(request):
    messages.add_message(
        request,
        messages.ERROR,
        _("You must evaluate minimum {} and maximum {} APDs").format(MIN_APDS, MAX_APDS)
    )


def _build_score_to_update(post_data, score):
    comments = _build_comments(post_data)
    objectives = _build_objectives(post_data)
    score = ScoreGet(
        student=score.student,
        period=score.period,
        cohort=score.cohort,
        comments=comments,
        objectives=objectives,
        **{key: post_data.get(key) for key in ScoreGet.attribute_map.keys() if key in post_data.keys()}
    )
    return score


def _build_comments(post_data):
    return {field: post_data.get(field) for field in COMMENTS_FIELDS}


def _build_objectives(post_data):
    apds_objectives = [post_data.get('obj-{}'.format(apd)) for apd in APDS]
    return {'apds': [only_number(apd) for apd in apds_objectives if apd]}


def _validate_score(post_data):
    apds_data = [post_data.get(apd) for apd in APDS if post_data.get(apd)]
    return MIN_APDS <= len(apds_data) <= MAX_APDS
