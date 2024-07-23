from django.templatetags.static import static

from django.contrib.auth.models import Group

import pandas as pd

from .models import Voter, Election
import random, string
from django.contrib.auth.models import User
import matplotlib.pyplot as plt
import numpy as np

import datetime
from django.utils import timezone

from .mail import gmail_authenticate, send_message

import datetime
from djui.settings import STATIC_DIR, MEDIA_ROOT
import os

def edit_voter(current_email, first_name, last_name, email):
    voter = Voter.objects.filter(email=current_email).first()

    if not voter:
        print("Voter does not exists. Creating")
        voter = Voter(first_name=first_name, last_name=last_name, email=email, organizational_id= "0")

    voter.first_name = first_name
    voter.last_name = last_name
    voter.email = email

    voter.save()

def create_voter(first_name, last_name, email):
    voter = Voter.objects.filter(email=email).first()
    voters_group = Group.objects.get(name='voter') 


    if not voter:
        print("Voter does not exists. Creating")
        voter = Voter(first_name=first_name, last_name=last_name, email=email, organizational_id= "0")
    else:
        print("Voter Exists. quitting!")
        return
    voter.ballot_id = get_random_number(7)
    voter.confirmation_code = get_random_string(12)

    if new_user := User.objects.filter(username=voter.email, is_active=True).first():
        # print(f" {voter.email} user found")
        new_user.groups.add(voters_group)
    else:
        new_user = User.objects.create_user(username=voter.email,
                                        first_name=voter.first_name,
                                        last_name=voter.last_name,
                                        email=voter.email,
                                        password="glass onion")
        new_user.groups.add(voters_group)
        new_user.save()
    voter.user = new_user
    voter.save()

def get_active_election():
    elections = Election.objects.all()
    if elections.count() == 0:
        return None
    else:
        # update_election_status(elections[0])
        return elections[0]

def handle_voter_list_upload(f):
    voters = []
    errors = []
    try:
        file_path = os.path.join(STATIC_DIR, "upload", f"{f.name}")
        # file_path = "/var/www/unio_vote/unio/static/upload/" + f.name
        with open(file_path,"wb+") as destination:  
            for chunk in f.chunks():  
                destination.write(chunk)  

        print("parsing to dataframe")
        df = pd.read_excel(file_path)
        # df = df.dropna()
        df = df.apply(lambda x: pd.Series(x.dropna().values))
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)

        # headers = ["first name", "last name", "email": "", "internal id": ""]
        print("starting to find unique voters")

        voters_email_set = set()
        voters_name_set = set()

        for index, row in df.iterrows():
            if index == 0: 
                # TODO:: validate the columns and email list
                continue    
            else:
                first_name = row[0]
                last_name = row[1]
                email = row[2]
                if len(row) > 3:
                    org_id = row[3]
                # print(first_name, last_name, email, org_id)
                name_key = first_name + "--" + last_name
                
                if email not in voters_email_set:
                    new_voter = Voter(first_name=first_name, last_name=last_name, email=email, organizational_id= org_id)
                    voters.append(new_voter)
                    voters_email_set.add(email)
                    voters_name_set.add(name_key)
                else:
                    print(f"error row = {index}")
                    errors.append(index)
        print("end if finding unique voters")
    except Exception as e:
        errors.append(-1)
    return voters, errors


def create_users_from_voters():
    voters = Voter.objects.all()
    new_voters_count = 0
    registered_voters_count = 0
    voters_group = Group.objects.get(name='voter') 
    voter_users_count = User.objects.filter(groups__name='voter').count()

    if voters.count() == 0:
        print("not voters to convert")
        return

    if voter_users_count > 0:
        print("already imported")
        return

    for voter in voters:
        if new_user := User.objects.filter(username=voter.email, is_active=True).first():
            # print(f" {voter.email} user found")
            new_user.groups.add(voters_group)
            registered_voters_count += 1
        else:
            new_voters_count += 1
            new_user = User.objects.create_user(username=voter.email,
                                            first_name=voter.first_name,
                                            last_name=voter.last_name,
                                            email=voter.email,
                                            password="glass onion")
            new_user.groups.add(voters_group)
            new_user.save()
        voter.user = new_user
        voter.save()
    print(f"New Voters: {new_voters_count}")
    print(f"Registered Voters: {registered_voters_count}")
# TODO:: test function. remove it.
def delete_all_elections():
    elections = Election.objects.all()
    if elections.count != 0:
        Election.objects.all().delete()

def delete_all_voters():
    all_voters = Voter.objects.all()
    if all_voters.count != 0:
        Voter.objects.all().delete()

    voter_users = User.objects.filter(groups__name='voter')
    if voter_users.count !=0:
        for v in voter_users:
            if not is_authority(v):
                v.delete()
            else:
                # TODO:: test
                group = Group.objects.get(name='voter') 
                v.groups.remove(group)



def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str

def get_random_number(length):
    result_str = ''.join((random.choice('0123456789') for i in range(length)))
    return result_str

def generate_piechart(file_name, labels, values):

    new_vals=[]
    new_labs = []
    new_cols = []
    colors = ['#99ff99','#ff9999','#66b3ff', "#000000"]

    for i in range(len(labels)):
        if values[i] != 0:
            new_vals.append(values[i])
            new_labs.append(labels[i])
            new_cols.append(colors[i])

    explode = None
    if len(new_vals) == 4:
        explode = (0.1, 0, 0, 0)
    if len(new_vals) == 3:
        explode = (0.1, 0, 0)
    elif len(new_vals) == 2:
        explode = (0.1, 0)


    y = np.array(new_vals)
    file_path = MEDIA_ROOT + 'upload/' + file_name
    print(file_path)
    
    plt.clf()


    if explode != None:
        plt.pie(y,labels = new_labs, explode=explode, startangle = 90, colors=new_cols)
    else:
        plt.pie(y,labels = new_labs, startangle = 90, colors=new_cols)

    plt.tight_layout()
    plt.savefig(file_path)

def update_election_status(election):

    voting_start_datetime = timezone.localtime(election.voting_start_datetime)

    voting_end_datetime = timezone.localtime(election.voting_end_datetime)

    now_zoned = timezone.localtime(timezone.now())

    notice_start_datetime = voting_start_datetime - datetime.timedelta(hours=election.notice_interval_hours)

    old_status = election.status

    if now_zoned - voting_end_datetime > datetime.timedelta(0):
        new_status = "t"
    elif now_zoned - voting_start_datetime > datetime.timedelta(0):
        new_status = "v"
    elif now_zoned - notice_start_datetime > datetime.timedelta(0):
        new_status = "n"
    else:
        new_status = "p"

    # if new_status != old_status:
    election.status = new_status

    election.save()

    return old_status, new_status


def send_notice_emails(election):

    service = gmail_authenticate()
    print("sending notice emails")
    all_voters = Voter.objects.all()

    to_tz = timezone.get_default_timezone()
    start_datetime = election.voting_start_datetime.astimezone(to_tz)
    for voter in all_voters:
        send_message(service, voter.email , "UNIO CSN-FSSS Election Notice", f' {voter.first_name} {voter.last_name},\nVous êtes invité à participer au scrutin qui se tiendra le {start_datetime.strftime("%Y-%m-%d %H:%M")}.\
Pour accéder au scrutin et à votre bulletin de vote, connectez-vous avec votre adresse courriel à https://unio.vote . \n \
\n\
\nUNIO\
\nAgora Vote inc.' )



    # print("Executing scheduled task now...")

def is_voter(user):
    return user.groups.filter(name='voter').exists()

def is_authority(user):
    return user.groups.filter(name='authority').exists()

def is_developer(user):
    return user.groups.filter(name='developer').exists()

