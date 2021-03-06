# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-03 08:04
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


def linkToDefaultCohort(apps, schema_editor):
    Cohort = apps.get_model("internship", "Cohort")
    StudentInformation = apps.get_model("internship", "InternshipStudentInformation")
    db_alias = schema_editor.connection.alias
    default_cohort = Cohort.objects.first()
    StudentInformation.objects.all().update(cohort=default_cohort)


class Migration(migrations.Migration):

    dependencies = [
        ('internship', '0014_period_cohort'),
    ]

    operations = [
        migrations.AddField(
            model_name='internshipstudentinformation',
            name='cohort',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='internship.Cohort'),
            preserve_default=False,
        ),
        migrations.RunPython(linkToDefaultCohort),
        migrations.AlterField(
            model_name='internshipstudentinformation',
            name='cohort',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='internship.Cohort'),
            preserve_default=False
        )
    ]
