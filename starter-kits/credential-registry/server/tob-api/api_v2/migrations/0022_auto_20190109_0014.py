# Generated by Django 2.0.10 on 2019-01-09 00:14

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("api_v2", "0021_auto_20190107_2203")]

    operations = [
        migrations.AddField(
            model_name="credentialtype",
            name="category_labels",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="credentialtype",
            name="claim_descriptions",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="credentialtype",
            name="claim_labels",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
