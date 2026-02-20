from django.urls import path
from . import views
from .feeds import LatestRun

app_name = 'speedrun'  # Namespace for this app's URLs

urlpatterns = [
    # List of all games
    path('', views.GameListView.as_view(), name='game_list'),

    # Submit a new speed run
    path('run/', views.submit_run, name='submit_run'),

    path('feed/',LatestRun(),name='run_feed'),

    # View details of a specific run
    path('run/<str:game>/<str:player_username>/<int:id>/', views.run_detail, name='run_detail'),

    # List of verified runs for a specific game
    path('<str:game>/', views.SpeedRunListView.as_view(), name='game_runs'),
]
