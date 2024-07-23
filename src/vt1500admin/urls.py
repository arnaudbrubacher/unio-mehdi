from django.urls import path

from . import views as app_views
from django.conf.urls.static import static 
from django.conf import settings

urlpatterns = [

    # TODO:: delete these two on production
    # path("setlang/<str:lang>/", app_views.SetLanguageView, name="set-language"),
    path("delete/", app_views.DeleteTestView, name="delete"),
    # path("usersfromvoters/", app_views.UsersFromVotersView, name="usersfromvoters"),
    path('dev/', app_views.VotersListView, name='voters'),

    path("login/", app_views.LoginWithLinkView, name="login2"),
    path('login-with-link/', app_views.MagicLinkLogin, name='magic'),

    path("create/", app_views.CreateElectionView, name="create"),
    # path("check/", app_views.CheckBallotView, name="check"),

    # path("ajax/voters/", voters_view, name="voters"),

    path("election/", app_views.ElectionView, name="election"),
    # path("elections/<int:pk>/", ElectionView, name="election"),
    path("results/", app_views.ResultsView, name="results"),

    path("vote/", app_views.BallotView, name="vote"),

    path('', app_views.index, name='index'),
    
    path('voter/', app_views.voter_view, name='voter'),
    path('authority-voter/', app_views.authority_voter_view, name='authority-voter'),
    path('authority/', app_views.authority_view, name='authority'),
    path('developer/', app_views.developer_view, name='developer'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
