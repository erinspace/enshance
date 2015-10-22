# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcid', '0003_auto_20151021_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='gatheredcontributor',
            name='provider_updated_date_time',
            field=models.DateTimeField(null=True),
        ),
    ]
