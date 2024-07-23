from django.db import models

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from datetime import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext as _

class LoginWithLink(models.Model):
    email = models.CharField(max_length=50, unique=True)


# TODO:: add validators

ANSWER_TYPE = (
    ('b', _('Abstention')),
    ('f', _('Pour')),
    ('a', _('Contre')),
)
class Ballot(models.Model):
    voter_id = models.ForeignKey("Voter", on_delete=models.RESTRICT, default=None)

    answer_1 = models.CharField(
        max_length=1,
        choices=ANSWER_TYPE,
        default="b",
        blank=False
    )


    answer_2 = models.CharField(
        max_length=1,
        choices=ANSWER_TYPE,
        default="b",
        blank=False
    )
    
    confirm_check = models.BooleanField(
        blank=False,
        default=False,
        help_text='Par la présente, je confirme que je soumets volontiers ce bulletin de vote.'
    )


class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
    ballot_id = models.CharField(max_length=30, default='N/A')
    confirmation_code = models.CharField(max_length=30, default='N/A')
    organizational_id = models.CharField(max_length=30, default='N/A', blank=True)
    first_name = models.CharField(max_length=50, default='N/A', blank=True)
    last_name = models.CharField(max_length=50, default='N/A', blank=True)
    email = models.CharField(max_length=50, default='N/A', blank=True)
    voted_at = models.DateTimeField(blank=True, default='2000-01-01 00:00')    
    is_voted = models.BooleanField(
        blank=False,
        default=False)
    vote_1 = models.CharField(
        max_length=1,
        choices=ANSWER_TYPE,
        blank=True
    )

    vote_2 = models.CharField(
        max_length=1,
        choices=ANSWER_TYPE,
        blank=True
    )

    def __str__(self):
        return f"Voter: first_name:{self.first_name}, last_name:{self.last_name}, organizational_id:{self.organizational_id}, email:{self.email}"

# class AccessToken(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, blank=True, null=True)
#     token_string = models.CharField(max_length=256, default='N/A', blank=True)
#     creation_datetime = models.DateTimeField(auto_now=True)    

#     def __str__(self):
#         return f"Extended User: access_token:{self.token_string}, first_name:{self.user.first_name}, last_name:{self.user.last_name}, email:{self.user.email}"

class VoterLog(models.Model):
    voter_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    VOTER_ACTION_TYPE = (
        ('s', 'signup'),
        ('l', 'login'),
        ('o', 'logout'),
        ('v', 'vote'),
        ('y', 'verify'),
        ('x', 'Reserved'),
    )

    action = models.CharField(
        max_length=1,
        choices=VOTER_ACTION_TYPE,
        blank=True,
        help_text='Voter Action Type',
    )

    metadata = models.CharField(max_length=200)
    action_datetime = models.DateTimeField()

class AuthorityLog(models.Model):
    authority_id = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    AUTHORITY_ACTION_TYPE = (
        ('s', 'signup'),
        ('l', 'login'),
        ('o', 'logout'),
        ('e', 'createElection'),
        ('v', 'vote'),
        ('y', 'verify'),
        ('x', 'Reserved'),
    )

    action = models.CharField(
        max_length=1,
        choices=AUTHORITY_ACTION_TYPE,
        blank=True,
        help_text='Authority Action Type',
    )

    metadata = models.CharField(max_length=200)
    action_datetime = models.DateTimeField()

class Election(models.Model):
    PHASE_TYPE = (
        ('p', 'configuration'),
        ('r', 'registration'),
        ('n', 'notice'),
        ('v', 'voter'),
        ('y', 'verification'),
        ('t', 'tally'),
        ('o', 'post-tally'),
        ('x', 'Reserved'),
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    question_1 = models.TextField(default="", blank=False)
    question_2 = models.TextField(default="", blank=False)

    creation_datetime = models.DateTimeField()

    status = models.CharField(
        max_length=1,
        choices=PHASE_TYPE,
        blank=False,
        default='p',
        help_text='Event Type'
    )

    notice_interval_hours = models.IntegerField(blank=True, default=24, validators=[MinValueValidator(1)])

    voting_start_datetime = models.DateTimeField(blank=True, default='2000-01-01 00:00')    
    voting_end_datetime = models.DateTimeField(blank=True, default='2000-01-01 00:00')

    results_pie_1 = models.ImageField(blank=True,upload_to='media/upload')
    results_pie_2 = models.ImageField(blank=True,upload_to='media/upload')
    # voters = models.ManyToManyField("Voter", blank=True)

    class Meta:
        unique_together = ("name", "question_1", "question_2")


class ElectionConfirm(models.Model):
    confirm_check = models.BooleanField(
        blank=False,
        default=False,
        help_text='Par la présente, je confirme que les informations électorales soumises sont légitimes et correctes.'
    )
    agreement_check = models.BooleanField(
        blank=False,
        default=False,
        help_text="Par la présente, je confirme que les informations électorales soumises sont légitimes et correctes. Par la présente, j'accepte et signe le contrat de licence de la demande de vote UNIO."
    )


class BallotCheck(models.Model):
    ballot_confirmation_code = models.CharField(max_length=30, default='N/A')

    cast_vote = models.CharField(
        max_length=1,
        choices=ANSWER_TYPE,
        blank=True
    )

    creation_datetime = models.DateTimeField()
