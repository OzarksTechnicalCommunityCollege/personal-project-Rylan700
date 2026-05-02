from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # student
    path('', views.event_feed, name='event_feed'),
    path('feed/', views.event_feed, name='event_feed_alt'),
    path('register/<int:event_id>/', views.register_event, name='register_event'),
    path('checkin/<int:event_id>/', views.check_in, name='check_in'),

    # club admin / staff
    path('create/', views.create_event, name='create_event'),
    path('submit/<int:event_id>/', views.submit_event, name='submit_event'),

    # attendance tracking
    path('attendance/<int:event_id>/', views.attendance_list, name='attendance_list'),
]