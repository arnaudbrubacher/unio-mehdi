# Generated by Django 4.2.4 on 2023-09-15 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vt1500admin", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="election",
            name="question_1",
            field=models.TextField(default="N/A"),
        ),
        migrations.AlterField(
            model_name="election",
            name="question_2",
            field=models.TextField(default="N/A"),
        ),
    ]