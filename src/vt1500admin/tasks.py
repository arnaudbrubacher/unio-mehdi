
from .functions import get_active_election, update_election_status,create_voter
from .functions import send_notice_emails, create_users_from_voters, edit_voter
from background_task import background
import datetime

from background_task.models import Task

@background(schedule=60)
def timer_task():
    tick_time = datetime.datetime.now()

    election = get_active_election()
    if election != None:
        old_status, new_status = update_election_status(election)
        print(f"Election Timer {tick_time}: election status: {old_status} to {new_status}")

        if old_status != new_status and new_status == "n":
            send_notice_emails(election)
    else:
        print(f"Election Timer {tick_time}: No election")

@background(schedule=60)
def create_users_task():
    tick_time = datetime.datetime.now()
    print(f"Voter Timer {tick_time}")
    create_users_from_voters()

@background(schedule=60)
def add_voter_task(first_name, last_name, email):
    tick_time = datetime.datetime.now()
    print(f"Create new Voter Timer {tick_time}")
    create_voter(first_name, last_name, email)

@background(schedule=60)
def edit_voter_task(old_email, first_name, last_name, email):
    tick_time = datetime.datetime.now()
    print(f"EditVoter Task {tick_time}")
    edit_voter(old_email, first_name, last_name, email)



Task.objects.all().delete()
timer_task(repeat=60,schedule=1)
create_users_task(repeat=300,schedule=1)
#add_voter_task("Célian", "Savard", "celianesavard@gmail.com",schedule=1)
#edit_voter_task("lynevilleneuve4@hotmail.com", "Lyne", "Villeneuve","lynevilleneuve4@hotmail.fr",schedule=1)
