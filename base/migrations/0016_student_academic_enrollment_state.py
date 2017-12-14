# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-20 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_offerenrollment_enrollment_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='academic_enrollment_state',
            field=models.CharField(blank=True, choices=[('SUBSCRIBED', 'SUBSCRIBED'), ('PROVISORY', 'PROVISORY')], max_length=15, null=True),
        ),
    ]