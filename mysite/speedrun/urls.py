from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .feeds import LatestRun

app_name = 'speedrun'  # Namespace for this app's URLs

urlpatterns = [
    # List of all games
    path('', views.GameListView.as_view(), name='game_list'),

    # User login/logout (built-in auth views)
    path('login/', auth_views.LoginView.as_view(template_name='speedrun/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/speedrun/'), name='logout'),

    # Submit a new speed run
    path('run/', views.submit_run, name='submit_run'),

    # Feed for latest runs
    path('feed/', LatestRun(), name='run_feed'),

    # User registration and edit
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),

    # View details of a specific run
    path('run/<str:game>/<str:player_username>/<int:id>/', views.run_detail, name='run_detail'),

    # List of verified runs for a specific game
    path('<str:game>/', views.SpeedRunListView.as_view(), name='game_runs'),
]