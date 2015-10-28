# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcid', '0006_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='gatheredcontributor',
            name='orcid_additional_name',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='gatheredcontributor',
            name='orcid_family_name',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='gatheredcontributor',
            name='orcid_given_name',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='gatheredcontributor',
            name='orcid_name',
            field=models.TextField(null=True),
        ),
    ]
