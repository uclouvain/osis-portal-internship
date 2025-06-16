##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.urls import include, path, re_path

from internship.views import main, hospital, resume, selection, score_encoding, place_evaluation
from internship.views.master_delegates import manage_delegates, new_delegate, delete_delegate

urlpatterns = [
    path('', main.view_internship_role_selection, name="internship"),

    path('student/', include([
        path('', main.view_cohort_selection, name="internship_cohort_selection"),
        re_path(r'^cohort/(?P<cohort_id>[\w\s-]+)/', include([
            path('', main.view_internship_student_home, name='internship_student_home'),
            path('selection/', include([
                path('', selection.view_internship_selection, name='select_internship'),
                path('ajax/selective_internship/', selection.get_selective_internship_preferences,
                    name='selective_internship_preferences'),
            ])),
            path('hospitals/', hospital.view_hospitals_list, name='hospitals_list'),
            path('resume/', resume.view_student_resume, name='student_resume'),
            path('place_evaluation/', include([
                path('', place_evaluation.view_place_evaluations_list, name='place_evaluation_list'),
                path(
                    '<uuid:affectation_uuid>',
                    place_evaluation.view_place_evaluation_form,
                    name='place_evaluation'
                )
            ])),
        ])),
    ])),

    path('master/', include([
        path('', main.view_internship_master_home, name='internship_master_home'),
        path('manage_delegates/', include([
            path('', manage_delegates, name='internship_manage_delegates'),
            re_path(r'new/(?P<specialty_uuid>[0-9a-f-]+)/(?P<organization_uuid>[0-9a-f-]+)/$', new_delegate,
                name='internship_new_delegate'),
            re_path(r'delete/(?P<allocation_uuid>[0-9a-f-]+)/$', delete_delegate,
                name='internship_delete_delegate'),
        ])),
        path('score_encoding/', include([
            path('', score_encoding.view_score_encoding, name="internship_score_encoding"),
            re_path(r'(?P<specialty_uuid>[0-9a-f-]+)/(?P<organization_uuid>[0-9a-f-]+)/', include([
                path('', score_encoding.view_score_encoding_sheet, name='internship_score_encoding_sheet'),
                re_path(r'^(?P<affectation_uuid>[0-9a-f-]+)/$',
                    score_encoding.view_score_encoding_form,
                    name="internship_score_encoding_form"),
            ])),
        ])),
    ])),

    path('ajax/', include([
       re_path(r'^(?P<affectation_uuid>[0-9a-f-]+)/validate$',
        score_encoding.score_encoding_validate, name="internship_score_encoding_validate"),
    ]))
]
