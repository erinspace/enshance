# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcid', '0004_gatheredcontributor_provider_updated_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gatheredcontributor',
            name='provider_updated_date_time',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
