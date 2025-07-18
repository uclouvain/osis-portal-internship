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
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk.models import ScoreGet

from base.views import layout
from internship.decorators.score_encoding_view_decorators import redirect_if_not_master, \
    redirect_if_not_master_with_matching_allocation
from internship.models.score_encoding_utils import DEFAULT_PERIODS, APDS, COMMENTS_FIELDS, MIN_APDS, MAX_APDS, \
    AVAILABLE_GRADES, APDS_DESCRIPTIONS, MAX_APDS_NEW
from internship.services.internship import InternshipAPIService
from internship.templatetags.selection_tags import only_number


@login_required
@redirect_if_not_master
def view_score_encoding(request):
    master = InternshipAPIService.get_master(person=request.user.person)
    allocations = InternshipAPIService.get_master_allocations(person=request.user.person, master_uuid=master['uuid'])
    for allocation in allocations:

        # get parent specialty details if subspecialty
        if allocation.specialty.parent:
            allocation.specialty = allocation.specialty.parent

        stats = InternshipAPIService.get_students_affectations_count(
            person=request.user.person,
            specialty_uuid=allocation['specialty']['uuid'],
            organization_uuid=allocation['organization']['uuid'],
        )
        allocation.__dict__['total_amount'] = stats['total_count']
        allocation.__dict__['amount_encoded'] = stats['validated_count']

    professional_malfunction_url = settings.OSIS_INTERNSHIP_PROFESSIONAL_MALFUNCTION_URL
    return layout.render(request, "internship_score_encoding.html", locals())


@login_required
@redirect_if_not_master_with_matching_allocation
def view_score_encoding_sheet(request, specialty_uuid, organization_uuid):
    if request.GET.get('period'):
        selected_period = request.GET.get('period', "")
    else:
        active_period = InternshipAPIService.get_active_period(request.user.person)
        selected_period = active_period['name'] if active_period else DEFAULT_PERIODS

    pagination_params = {'limit': int(request.GET.get('limit', '0')), 'offset': int(request.GET.get('offset', '0'))}

    apds = APDS

    specialty = InternshipAPIService.get_specialty(request.user.person, specialty_uuid)
    organization = InternshipAPIService.get_organization(request.user.person, organization_uuid)

    students_affectations, previous, next, count = InternshipAPIService.get_paginated_students_affectations(
        person=request.user.person,
        specialty_uuid=specialty_uuid,
        organization_uuid=organization_uuid,
        period=selected_period,
        **pagination_params
    )

    for affectation in students_affectations:
        if affectation.period.is_preconcours:
            affectation.has_apd = False
        else:
            affectation.has_apd = True

    not_validated_count = len(
        [
            _ for affectation in students_affectations
            if affectation.score and not affectation.score.validated or not affectation.score
        ]
    )
    periods = InternshipAPIService.get_periods(person=request.user.person, cohort_name=organization.cohort.name)
    if periods:
        periods = sorted(periods, key=lambda p: p.date_end)

    return layout.render(request, "internship_score_encoding_sheet.html", locals())


@login_required
@redirect_if_not_master_with_matching_allocation
def view_score_encoding_form(request, specialty_uuid, organization_uuid, affectation_uuid):
    affectation = InternshipAPIService.get_affectation(request.user.person, affectation_uuid)
    period = affectation.period
    student = affectation.student

    score = InternshipAPIService.get_score(request.user.person, affectation_uuid)
    specialty = InternshipAPIService.get_specialty(request.user.person, specialty_uuid)
    organization = InternshipAPIService.get_organization(request.user.person, organization_uuid)

    internship = InternshipAPIService.get_internship(request.user.person, affectation.internship_uuid)

    apds = APDS
    apds_descriptions = APDS_DESCRIPTIONS
    comments_fields = COMMENTS_FIELDS
    available_grades = AVAILABLE_GRADES

    if request.POST:
        score = _build_score_to_update(request.POST, score)
        if not _validate_score(request, internship, period) or not _required_response(request, period):
            return layout.render(request, "internship_score_encoding_form.html", locals())
        if InternshipAPIService.update_score(request.user.person, affectation_uuid, score):
            _show_success_update_msg(request, period, student)
            if request.POST.get("btn-save-validate"):
                score_encoding_validate(request, affectation_uuid)
            return redirect(reverse('internship_score_encoding_sheet', kwargs={
                'specialty_uuid': specialty_uuid,
                'organization_uuid': organization_uuid,
            }) + '?period={}'.format(period.name))
        messages.add_message(request, messages.ERROR, _('An error occurred during score update'))

    if period.is_preconcours:
        template_name = "internship_score_encoding_form_preconcours.html"
    else:
        template_name = "internship_score_encoding_form.html"

    return layout.render(request, template_name, {**locals(), 'score': score})


@login_required
@redirect_if_not_master
def score_encoding_validate(request, affectation_uuid):
    data, status, headers = InternshipAPIService.validate_internship_score(request.user.person, affectation_uuid)
    is_success = status == 204
    return JsonResponse({} if is_success else {'error': _('An error occured during validation')})


def _show_success_update_msg(request, period, student):
    messages.add_message(
        request,
        messages.SUCCESS,
        _("Score updated successfully for {}'s internship during {}").format(
            student.last_name, period.name
        )
    )


def _show_invalid_update_msg(request, min_apds, max_apds):
    messages.add_message(
        request,
        messages.ERROR,
        _("You must evaluate minimum {} and maximum {} EPAs").format(min_apds, max_apds)
    )


def _show_required_apd_msg(request, mandatory_apds):
    mandatory_apds_string = ', '.join([str(apd) for apd in mandatory_apds])
    messages.add_message(
        request,
        messages.ERROR,
        _("An evaluation for the following EPAs is required: {}").format(mandatory_apds_string)
    )


def _show_required_response_msg(request):
    messages.add_message(
        request,
        messages.ERROR,
        _("You must reply to the required question about internship student attendance during evaluation")
    )


def _build_score_to_update(post_data, score):
    comments = _build_comments(post_data)
    objectives = _build_objectives(post_data)

    behavior_score = float(post_data.get('behavior_score')) if 'behavior_score' in post_data else None
    competency_score = float(post_data.get('competency_score')) if 'competency_score' in post_data else None

    preconcours_evaluation_detail = {
        key: value for key, value in post_data.items()
        if key not in ['behavior_score', 'competency_score', 'csrfmiddlewaretoken', 'btn-save-validate']
    }

    score = ScoreGet(
        uuid=score.uuid,
        comments=comments,
        objectives=objectives,
        student_presence=post_data.get('presence') == 'yes',
        behavior_score=behavior_score,
        competency_score=competency_score,
        preconcours_evaluation_detail=preconcours_evaluation_detail,
        **{key: post_data.get(key) for key in ScoreGet.attribute_map.keys() if key in post_data.keys() and key not in [
            'behavior_score', 'competency_score'
        ]}
    )
    return score


def _build_comments(post_data):
    return {field_id: post_data.get(field_id) for field_id, field_label in COMMENTS_FIELDS}


def _build_objectives(post_data):
    apds_objectives = [post_data.get('obj-{}'.format(apd)) for apd in APDS]
    return {'apds': [only_number(apd) for apd in apds_objectives if apd]}


def _validate_score(request, internship, period):
    if period.is_preconcours:
        # Validate preconcours form
        if not request.POST.get('competency_score') and request.POST.get('behavior_score'):
            messages.add_message(
                request, messages.ERROR, _("Please provide at least competency score and behavior score.")
            )
            return False
        return True
    else:
        mandatory_apds = internship.apds
        max_apds = MAX_APDS if internship.cohort.parent_cohort is None else MAX_APDS_NEW
        apds_data = [apd for apd in APDS if request.POST.get(apd)]

        # number of evaluated apds should be between min and max
        if not MIN_APDS <= len(apds_data) <= max_apds:
            _show_invalid_update_msg(request, MIN_APDS, max_apds)
            return False

        # mandatory apds should be evaluated
        for apd in mandatory_apds:
            if f"apd_{apd}" not in apds_data:
                _show_required_apd_msg(request, mandatory_apds)
                return False

        return True
    return True


def _required_response(request, period):
    if not request.POST.get('presence') and not period.is_preconcours:
        _show_required_response_msg(request)
        return False
    return True
