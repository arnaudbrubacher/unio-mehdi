# Generated by Django 4.2.5 on 2023-09-21 01:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vt1500admin', '0013_alter_election_notice_interval_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='notice_interval_hours',
            field=models.IntegerField(blank=True, default=24, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]