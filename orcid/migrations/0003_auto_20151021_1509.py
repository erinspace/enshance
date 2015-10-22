# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcid', '0002_auto_20151021_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='additional_name',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='family_name',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='given_name',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='id_email',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='institution',
            field=models.TextField(null=True),
        ),
    ]
