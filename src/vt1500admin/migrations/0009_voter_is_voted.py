# Generated by Django 4.2.4 on 2023-09-16 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "vt1500admin",
            "0008_voter_voted_at_alter_election_voting_end_datetime_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="voter",
            name="is_voted",
            field=models.BooleanField(default=False),
        ),
    ]
