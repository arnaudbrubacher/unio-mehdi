from django import forms
from .models import Election, Ballot, ElectionConfirm, LoginWithLink, BallotCheck
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.DateInput):
    input_type = 'time'

class BallotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
    class Meta:
        model = Ballot
        fields = ['answer_1', 'answer_2',"confirm_check"]
        widgets = {
            'answer_1': forms.RadioSelect(),
            'answer_2': forms.RadioSelect(),
            'confirm_check': forms.CheckboxInput(attrs={'id': 'check'})
        }
        labels = {
            "answer_1": "Please enter your vote for Question #1",
            "answer_2": "Please enter your vote for Question #2",
            "confirm_check": ""
        }

class ElectionCreateForm(forms.ModelForm):

    voters_file = forms.FileField(validators=[
        FileExtensionValidator(allowed_extensions=['xlsx'])], label="Liste électorale (fichier .xlsx)")

    voting_starts_at = forms.DateField(widget=DateInput())  
    voting_start_time = forms.TimeField(widget=TimeInput())  
    voting_ends_at = forms.DateField(widget=DateInput())  
    voting_end_time = forms.TimeField(widget=TimeInput())  
    class Meta:
        model = Election
        fields = ['question_1', 'question_2', 'notice_interval_hours', 'description']
        widgets = {
        }

        labels = {
                    "question_1": "Question 1",
                    "question_2": "Question 2",
                    "notice_interval_hours": "Délai de préavis avant de voter (heures)"
                }
    field_order = ['question_1','question_2',  'description', 'voting_starts_at', 'voting_start_time', 'voting_ends_at', 'voting_end_time','notice_interval_hours', 'voters_file']


class ElectionConfirmForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
    class Meta:
        model = ElectionConfirm
        fields = ['confirm_check', 'agreement_check']
        labels = {
                    "confirm_check": "",
                    "agreement_check": ""
                }

class LoginWithLinkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
    class Meta:
        model = LoginWithLink
        fields = ['email']


class BallotCheckForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True
    class Meta:
        model = BallotCheck
        fields = ['ballot_confirmation_code']
        labels = {
                    "ballot_confirmation_code": "",
                }
