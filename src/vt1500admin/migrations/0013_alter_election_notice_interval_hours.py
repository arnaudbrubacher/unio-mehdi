# Generated by Django 4.2.5 on 2023-09-20 22:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vt1500admin', '0012_alter_ballot_answer_1_alter_ballot_answer_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='notice_interval_hours',
            field=models.IntegerField(blank=True, default=24, validators=[django.core.validators.MinValueValidator(2)]),
        ),
    ]
