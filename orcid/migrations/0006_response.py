# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orcid', '0005_auto_20151022_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('key', models.TextField(serialize=False, primary_key=True)),
                ('method', models.CharField(max_length=8)),
                ('url', models.TextField()),
                ('ok', models.NullBooleanField()),
                ('content', models.BinaryField(null=True)),
                ('encoding', models.TextField(null=True)),
                ('headers_str', models.TextField(null=True)),
                ('status_code', models.IntegerField(null=True)),
                ('time_made', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
