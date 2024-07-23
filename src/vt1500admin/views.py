
# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from .forms import ElectionCreateForm, BallotForm, ElectionConfirmForm, LoginWithLinkForm, BallotCheckForm
from .functions import handle_voter_list_upload, delete_all_elections, delete_all_voters, get_random_number, get_active_election
from .functions import get_random_string, generate_piechart, update_election_status, create_users_from_voters
from .models import Election, Voter
from .tables import ElectionTable, VotersTable
# from .guard import ELECTION_RUNTIME
import datetime  
import json

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.models import Sum
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core import signing
import base64
from urllib.parse import urlencode, unquote_plus
from .mail import gmail_authenticate, build_message, send_message
from django.contrib.auth import login, logout

from .functions import is_voter, is_authority, is_developer

from django.forms.utils import ErrorList
from django.utils import translation
# from django.utils.translation import LANGUAGE_SESSION_KEY

from django.core.paginator import Paginator
from djui.settings import STATIC_DIR, MEDIA_ROOT

import os
LANGUAGE_SESSION_KEY = '_language'

@login_required
@user_passes_test(is_developer)
def DeleteTestView(request):
    result1_path = os.path.join(MEDIA_ROOT,'upload', 'piechart_1.png')
    result2_path = os.path.join(MEDIA_ROOT,'upload', 'piechart_2.png')
    print(result1_path)
    print(result2_path)

    if os.path.isfile(result1_path):
        os.remove(result1_path)
        print("removing result_1")
    if os.path.isfile(result2_path) :
        os.remove(result2_path)
        print("removing result_2")

    delete_all_elections()
    delete_all_voters()

    return HttpResponseRedirect(reverse('index'))

@login_required
@user_passes_test(is_developer)
def UsersFromVotersView(request):
    create_users_from_voters()
    return HttpResponse("done")

@login_required
def SetLanguageView(request, lang):
    translation.activate(lang)
    request.session[LANGUAGE_SESSION_KEY] = lang
    # I use HTTP_REFERER to direct them back to previous path 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@user_passes_test(is_voter)
def CheckBallotView(request):
    election = get_active_election()
    if request.method == 'POST':
        form = BallotCheckForm(request.POST, request.FILES)
        if form.is_valid():
            pass

        code = form.cleaned_data['ballot_confirmation_code']
        if voter := Voter.objects.filter(confirmation_code=code).first():
            context = {"election": election, "form": form, "confirm_status": 1, "vote": voter.vote}
        else:
            context = {"election": election, "form": form, "confirm_status": 2}

        template = "ballot-check.html"
        return render(request, template, context)  

    form = BallotCheckForm(initial={'ballot_confirmation_code': ''})
    context = {"election": election, "form": form, "confirm_status": 0}

    template = "ballot-check.html"
    return render(request, template, context)  
    # return HttpResponseRedirect(reverse('index'))

def MagicLinkLogin(request):
    # if request.method == "GET":
    #     return render(request, "login2.html")
    token = request.GET.get("token")
    if not token:
        # Go back to main page; alternatively show an error page
        return HttpResponseRedirect(reverse('index'))

    data = signing.loads(token, max_age=3600)
    email = data.get("email")
    if not email:
        return HttpResponseRedirect(reverse('index'))

    user = User.objects.filter(username=email, is_active=True).first()
    if not user:
        # user does not exist or is inactive
        return HttpResponseRedirect(reverse('index'))

    # validate token and check for expiry; we want to make sure
    # it's only been generated since the last login
    if user.last_login:
        delta = timezone.now() - user.last_login
        try:
            data = signing.loads(token, max_age=delta)
        except signing.SignatureExpired:
            # signature expired, redirect to main page or show error page.
            return HttpResponseRedirect(reverse('index'))

    login_state = data.get("login_state")
    session_login_state = request.session.get("login_state")

    if not login_state or not session_login_state:
        return HttpResponseRedirect(reverse('index'))

    if login_state != session_login_state:
        return HttpResponseRedirect(reverse('index'))

    # Everything checks out, log the user in and redirect to dashboard!
    login(request, user, backend='vt1500admin.backends.TokenBackend')
    return HttpResponseRedirect(reverse('index'))


def LoginWithLinkView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.POST:
        email = request.POST.get("email")
        if user := User.objects.filter(username=email, is_active=True).first(): 
            random_string = get_random_string(16)
            request.session["login_state"] = random_string
            token = signing.dumps({"email": email, "login_state": random_string})
            qs = urlencode({"token": token})

            magic_link = request.build_absolute_uri(
                location=reverse("magic"),
            ) + f"?{qs}"

            service = gmail_authenticate()
            send_message(service, email, "UNIO Login Link", f'Voici votre lien de connexion pour accéder à UNIO: \n{magic_link}\n\nUNIO\nAgora Vote Inc.' )
        elif user := User.objects.filter(username=email.upper(), is_active=True).first():
            random_string = get_random_string(16)
            request.session["login_state"] = random_string
            token = signing.dumps({"email": email.upper(), "login_state": random_string})
            qs = urlencode({"token": token})

            magic_link = request.build_absolute_uri(
                location=reverse("magic"),
            ) + f"?{qs}"

            service = gmail_authenticate()
            send_message(service, email, "UNIO Login Link", f'Voici votre lien de connexion pour accéder à UNIO: \n{magic_link}\n\nUNIO\nAgora Vote Inc.' )

        context = {}
        template = "login-sent.html"
        return render(request, template, context)  
        # return HttpResponseRedirect(reverse('index'))
    # return render(request, 'home.html', {})
    form = LoginWithLinkForm()
    context = {"form": form}

    template = "login2.html"
    return render(request, template, context)  


@login_required
@user_passes_test(is_authority)
def CreateElectionView(request):

    election = get_active_election()

    voters_list = Voter.objects.all()
    paginator = Paginator(voters_list, 1500)
    page = request.GET.get('page', 1)
    try:
        voters_page = paginator.page(page)
    except PageNotAnInteger:
        voters_page = paginator.page(1)
    except EmptyPage:
        voters_page = paginator.page(paginator.num_pages)   

    if request.method == 'POST':
        form = ElectionCreateForm(request.POST, request.FILES,instance= election)
        # print(form)
        if form.is_valid():
            # delete_all_elections()
            voters, errors = handle_voter_list_upload(request.FILES['voters_file'])

            if len(voters) == 0:
                file_errors = form._errors.setdefault("voters_file", ErrorList())
                file_errors.append(u"Elections with zero number of voters are not allowed.")
                return render(request, 'create.html', {'form': form, 'election': election})

            if len(errors) != 0:
                file_errors = form._errors.setdefault("voters_file", ErrorList())
                if errors[len(errors) - 1] == -1: 
                    file_errors.append(u"List formatting error. Please follow the format of sample excel file.")
                else:
                    file_errors.append(u"Please remove the duplicate voters.")
  
                return render(request, 'create.html', {'form': form, 'election': election, "voters": voters_list, "voters_page":voters_page})

            # TODO:: for single election setup

            description = form.cleaned_data['description']
            question_1 = form.cleaned_data['question_1']
            question_2 = form.cleaned_data['question_2']
            current_phase = 'p'

            voting_start_datetime= datetime.datetime.combine(form.cleaned_data['voting_starts_at'], form.cleaned_data['voting_start_time'])
            voting_end_datetime= datetime.datetime.combine(form.cleaned_data['voting_ends_at'], form.cleaned_data['voting_end_time'])
            notice_interval_hours = form.cleaned_data['notice_interval_hours']

            name = "election" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            
            now_zoned = datetime.datetime.now()
            time_change = datetime.timedelta(hours=1)
            notice_time_change = datetime.timedelta(hours=notice_interval_hours)

            voting_start_errors = form._errors.setdefault("voting_starts_at", ErrorList())
            voting_end_errors = form._errors.setdefault("voting_ends_at", ErrorList())
            notice_interval_errors = form._errors.setdefault("notice_interval_hours", ErrorList())

            #if voting_start_datetime - notice_time_change < now_zoned:
            #    notice_interval_errors.append("Notice period's start date/time can not be in the past.")
            #    return render(request, 'create.html', {'form': form, 'election': election})

            #if voting_start_datetime < now_zoned :
            #    voting_start_errors.append("Voting start date/time can not be in the past.")
            #    return render(request, 'create.html', {'form': form, 'election': election})

            #if voting_end_datetime < voting_start_datetime + time_change:
            #    voting_end_errors.append("Voting duration must be at least at hour.")
            #    return render(request, 'create.html', {'form': form, 'election': election})

            if election == None:
                election = Election(name=name, description=description, creation_datetime=timezone.make_aware(datetime.datetime.now()),
                             question_1=question_1,
                             question_2=question_2,
                             voting_start_datetime=voting_start_datetime,
                             voting_end_datetime=voting_end_datetime,
                             notice_interval_hours=notice_interval_hours
                             )
            else:
                election.name = name    
                election.question_1 = question_1    
                election.question_2 = question_2    
                election.description = description    
                election.voting_start_datetime = voting_start_datetime
                election.voting_end_datetime = voting_end_datetime
                election.notice_interval_hours = notice_interval_hours
            election.save()

            print("deleting voters")
            delete_all_voters()

            # print("Saving voters")
            print("creating new voters voters")

            for voter in voters:
                # print(voter.email)
                # if new_user := User.objects.filter(username=voter.email, is_active=True).first():
                #     # print(f" {voter.email} user found")
                #     new_user.groups.add(voters_group)
                # else:
                # print(f" {voter.email} user not found")
                # new_user = User.objects.create_user(username=voter.email,
                #                                 first_name=voter.first_name,
                #                                 last_name=voter.last_name,
                #                                 email=voter.email,
                #                                 password='glass onion')
                # new_user.groups.add(voters_group)
                # new_user.save()
                # voter.user = new_user
                voter.ballot_id = get_random_number(7)
                voter.confirmation_code = get_random_string(12)
                voter.save()

            # ELECTION_RUNTIME.setup_election(p, voters)
            voters_list = Voter.objects.all()
            paginator = Paginator(voters_list, 1500)
            page = request.GET.get('page', 1)
            try:
                voters_page = paginator.page(page)
            except PageNotAnInteger:
                voters_page = paginator.page(1)
            except EmptyPage:
                voters_page = paginator.page(paginator.num_pages) 
            confirm_form = ElectionConfirmForm()
            context = {"election":election, "form": confirm_form, "voters": voters_list, "voters_page":voters_page}

            template = "create2.html"
            return render(request, template, context)
        else:
            return render(request, 'create.html', {'form': form, 'election': election, "voters_page":voters_page})

    else: # Not POST

        election = get_active_election()
        
        # now_zoned = timezone.make_aware(datetime.datetime.now())
        now_zoned = datetime.datetime.now()
        now_zoned_time = now_zoned.strftime("%H:%M:%S")
        time_change = datetime.timedelta(hours=1)
        if election != None:
            to_tz = timezone.get_default_timezone()
            start_datetime = election.voting_start_datetime.astimezone(to_tz)

            starts_at = start_datetime.strftime("%Y-%m-%d")
            starts_at_time = start_datetime.strftime("%H:%M")
            end_datetime = election.voting_end_datetime.astimezone(to_tz)
            ends_at = end_datetime.strftime("%Y-%m-%d")
            ends_at_time = end_datetime.strftime("%H:%M")

            form = ElectionCreateForm(instance=election, initial={'voting_starts_at': starts_at,
                                               'voting_ends_at': ends_at,
                                               'voting_start_time': starts_at_time,
                                               'voting_end_time': ends_at_time
                                               })
        else:

            form = ElectionCreateForm(initial={'voting_starts_at': (now_zoned + time_change).strftime("%Y-%m-%d"),
                                               'voting_ends_at': (now_zoned + time_change + time_change).strftime("%Y-%m-%d"),
                                               'voting_start_time': (now_zoned + time_change).strftime("%H:%M"),
                                               'voting_end_time': (now_zoned + time_change + time_change).strftime("%H:%M")
                                               })
        return render(request, 'create.html', {'form': form, 'election': election, "voters": voters_list})
 

@login_required
@user_passes_test(is_developer)
def VotersListView(request):
    voters_list = Voter.objects.all()
    paginator = Paginator(voters_list, 1500)
    page = request.GET.get('page', 1)

    try:
        voters = paginator.page(page)
    except PageNotAnInteger:
        voters = paginator.page(1)
    except EmptyPage:
        voters = paginator.page(paginator.num_pages)
    return render(request, 'voters-list.html', {'voters': voters})

@login_required
def ElectionView(request):
    if is_voter(request.user):
        voter = Voter.objects.filter(user=request.user)[0]
    else:
        voter = None
    elections = Election.objects.all()

    if elections.count() != 0:
        election = elections[0]
        # timer_task()

        # election.status = update_election_status(election)
        # election.save()
        # voters = Voter.objects.all()
        voters_list = Voter.objects.all()
        voters_count = voters_list.count()
        paginator = Paginator(voters_list, 1500)
        page = request.GET.get('page', 1)

        try:
            voters = paginator.page(page)
        except PageNotAnInteger:
            voters = paginator.page(1)
        except EmptyPage:
            voters = paginator.page(paginator.num_pages)
        return render(request, 'election.html', {'election': election, 'voters': voters, 'voter':voter, "voters_count": voters_count, 'is_authority': is_authority(request.user), 'is_voter': is_voter(request.user)})
    else:
        return HttpResponseRedirect(reverse('index'))

@login_required
@user_passes_test(is_authority)
def ResultsView(request):
    election = Election.objects.all()[0]
    voters = Voter.objects.all()
    
    for_count_1 = 0
    against_count_1 = 0
    abs_count_1 = 0
    null_count_1 = 0

    for_count_2 = 0
    against_count_2 = 0
    abs_count_2 = 0
    null_count_2 = 0


    for voter in voters:
        if voter.vote_1 == 'f':
            for_count_1 += 1
        elif voter.vote_1 == 'a':
            against_count_1 += 1
        elif voter.vote_1 == 'b':
            abs_count_1 += 1
        else:
            null_count_1 += 1
        
        if voter.vote_2 == 'f':
            for_count_2 += 1
        elif voter.vote_2 == 'a':
            against_count_2 += 1
        elif voter.vote_2 == 'b':
            abs_count_2 += 1
        else:
            null_count_2 += 1

    null_count_1 = voters.count() - (for_count_1 + against_count_1 + abs_count_1)
    null_count_2 = voters.count() - (for_count_2 + against_count_2 + abs_count_2)

    result1_path = os.path.join(MEDIA_ROOT,'upload', 'piechart_1.png')
    result2_path = os.path.join(MEDIA_ROOT,'upload', 'piechart_2.png')
    print(result1_path)
    print(result2_path)

    if not os.path.isfile(result1_path) or not os.path.isfile(result2_path) :
        print("generating")
        generate_piechart("piechart_1.png",["For_Votes","Against_Votes","Abstention","Not-Attended"], [for_count_1, against_count_1, abs_count_1, null_count_1])
        generate_piechart("piechart_2.png", ["For_Votes","Against_Votes","Abstention","Not-Attended"], [for_count_2, against_count_2, abs_count_2, null_count_2])
        election.results_pie_1 = 'upload/piechart_1.png'
        election.results_pie_2 = 'upload/piechart_2.png'
        election.save()
    else:
        print("not generating")

    return render(request, 'results.html', {'election': election, 'voters': voters, "for_count_1": for_count_1, "against_count_1": against_count_1, "abs_count_1": abs_count_1, "null_count_1": null_count_1, "for_count_2": for_count_2, "against_count_2": against_count_2, "abs_count_2": abs_count_2, "null_count_2": null_count_2})

@login_required
@user_passes_test(is_voter)
def BallotView(request):
    # timer_task()

    election = get_active_election()
    voter = Voter.objects.filter(user=request.user)[0]
    if election != None:
        if election.status == "p" and election.status == "n" :
            print(voter.vote_1)
            if not voter.is_voted:
                
                if request.method == 'POST':
                    form = BallotForm(request.POST)
                    if form.is_valid():
                        answer_1 = form.cleaned_data['answer_1']
                        answer_2 = form.cleaned_data['answer_2']
                        voter.vote_1 = answer_1
                        voter.vote_2 = answer_2
                        voter.is_voted = True
                        voter.voted_at = datetime.datetime.now()
                        voter.save()
                        context = {'ballot_id': voter.ballot_id, 'election': election, 'voter': voter, 'just_voted': "YES"}
                        template = "ballot2.html"
                    return render(request, template, context)       
                else:
                    form = BallotForm()

                    context = {'form': form, 'ballot_id': voter.ballot_id, 'election': election, 'voter': voter}
                    template = "ballot.html"
                    return render(request, template, context)
            else:
                context = {'ballot_id': voter.ballot_id, 'election': election, 'voter': voter}
                template = "ballot2.html"
                return render(request, template, context)
        else:
            context = {'election': election, 'voter': voter}
            template = "ballot0.html"
            return render(request, template, context)

    else:
        return HttpResponseRedirect(reverse('index'))

@login_required
def index(request):
    groups = request.user.groups.filter(user=request.user)

    if is_voter(request.user):
        if is_authority(request.user):
            return HttpResponseRedirect(reverse('authority-voter'))
        else:
            return HttpResponseRedirect(reverse('voter'))
    elif is_authority(request.user):
        return HttpResponseRedirect(reverse('authority'))
    elif is_developer(request.user):
        return HttpResponseRedirect(reverse('developer'))

    context = {}
    
    raise PermissionDenied()


@login_required
@user_passes_test(is_voter)
def voter_view(request):

    voter = Voter.objects.filter(user=request.user)[0]

    elections = Election.objects.all()
    if elections.count() != 0: 
        election = elections[0]

        context = {"election": election, "user": request.user, "voter":voter}
        template = "voter-home.html"
        return render(request, template, context)
    else:
        return HttpResponseRedirect(reverse('index'))

@login_required
@user_passes_test(is_authority)
def authority_view(request):
    election = get_active_election()

    context = {"user": request.user, "election": election}
    template = "auth-home.html"
    return render(request, template, context)

@login_required
@user_passes_test(is_authority)
# @user_passes_test(is_voter)
def authority_voter_view(request):
    election = get_active_election()
    # voter = Voter.objects.filter(user=request.user)[0]
    voter = None
    context = {"user": request.user, "election": election, "voter": voter}
    template = "auth-voter-home.html"
    return render(request, template, context)
@login_required
@user_passes_test(is_developer)
def developer_view(request):
    context = {}
    template = "base.html"
    return render(request, template, context)

@login_required
def import_voters_view(request):
    form_string = request.POST.get('form')

    form_dict = json.loads(form_string)
    name = form_dict[1]["value"]
    question = form_dict[2]["value"]
    notice_interval_hours = form_dict[3]["value"]

    voting_start_date = form_dict[4]["value"]
    voting_start_time = form_dict[5]["value"]
    voting_end_date = form_dict[6]["value"]
    voting_end_time = form_dict[7]["value"]
    description  = form_dict[8]["value"]

    election = Election(name=name,
                        question=question,
                        notice_interval_hours=notice_interval_hours,
                        voting_start_date=voting_start_date,
                        voting_start_time=voting_start_time,
                        voting_end_date=voting_end_date,
                        voting_end_time=voting_end_time,
                        description=description)

    confirm_form = ElectionConfirmForm()

    context = {"election":election, "form": confirm_form, "voters": None}

    template = "create2.html"
    return render(request, template, context)
