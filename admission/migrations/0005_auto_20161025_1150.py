# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-25 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0004_profession_adhoc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='secondaryeducation',
            name='international_diploma',
            field=models.CharField(blank=True, choices=[('NATIONAL', 'baccalaureat_national'), ('EUROPEAN', 'baccalaureat_european'), ('INTERNATIONAL', 'baccalaureat_international')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='secondaryeducation',
            name='result',
            field=models.CharField(blank=True, choices=[('LOW', 'low_result'), ('MIDDLE', 'middle_result'), ('HIGH', 'high_result')], max_length=20, null=True),
        ),
    ]