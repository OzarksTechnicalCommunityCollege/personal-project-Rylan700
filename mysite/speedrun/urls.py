from django.urls import path
from . import views

app_name = 'speedrun'
urlpatterns = [
    # post views
    path('', views.speed_run_list, name='run_list'),
    path('<int:id>/', views.run_detail, name='run_detail'),
]
