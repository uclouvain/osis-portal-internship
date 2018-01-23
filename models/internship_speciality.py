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
from osis_common.models.serializable_model import SerializableModelAdmin, SerializableModel
from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class InternshipSpecialityAdmin(SerializableModelAdmin):
    list_display = ('name', 'acronym', 'cohort')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'cohort')}),)


class InternshipSpeciality(SerializableModel):
    name = models.CharField(max_length=125, blank=False, null=False)
    acronym = models.CharField(max_length=125, blank=False, null=False)
    cohort = models.ForeignKey('internship.Cohort', null=False)

    def __str__(self):
        return u"%s" % self.name


def find_by_id(a_id):
    try:
        return InternshipSpeciality.objects.get(id=a_id)
    except ObjectDoesNotExist:
        return None


def find_all():
    return InternshipSpeciality.objects.all()


def filter_by_cohort(cohort):
    return InternshipSpeciality.objects.filter(cohort=cohort)