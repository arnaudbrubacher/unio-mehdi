# Generated by Django 4.2.5 on 2023-09-19 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vt1500admin', '0009_voter_is_voted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='status',
            field=models.CharField(choices=[('p', 'configuration'), ('r', 'registration'), ('n', 'notice'), ('v', 'voter'), ('y', 'verification'), ('t', 'tally'), ('o', 'post-tally'), ('x', 'Reserved')], default='p', help_text='Event Type', max_length=1),
        ),
        migrations.AlterField(
            model_name='electionconfirm',
            name='agreement_check',
            field=models.BooleanField(default=False, help_text="Par la présente, je confirme que les informations électorales soumises sont légitimes et correctes. Par la présente, j'accepte et signe le contrat de licence de la demande de vote UNIO."),
        ),
        migrations.AlterField(
            model_name='electionconfirm',
            name='confirm_check',
            field=models.BooleanField(default=False, help_text='Par la présente, je confirme que les informations électorales soumises sont légitimes et correctes.'),
        ),
    ]
