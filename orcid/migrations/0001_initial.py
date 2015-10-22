# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GatheredContributor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_name', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('family_name', models.CharField(max_length=255, null=True)),
                ('given_name', models.CharField(max_length=255, null=True)),
                ('additional_name', models.CharField(max_length=255, null=True)),
                ('institution', models.CharField(max_length=255, null=True)),
                ('id_osf', models.CharField(max_length=10, null=True)),
                ('id_orcid', models.CharField(max_length=100, null=True)),
                ('id_email', models.CharField(max_length=255, null=True)),
                ('raw_orcid', django_pgjson.fields.JsonField(null=True)),
                ('source', models.CharField(max_length=255)),
                ('docID', models.TextField()),
            ],
        ),
    ]
