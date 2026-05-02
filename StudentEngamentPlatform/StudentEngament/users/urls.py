from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "users"

# =========================
# USER PROFILE SYSTEM
# =========================
urlpatterns = [

    path("profile/<int:user_id>/", views.user_profile, name="user_profile"),
    path("badges/<int:user_id>/", views.user_badges, name="user_badges"),
    path("activity/<int:user_id>/", views.user_activity, name="user_activity"),

    # =========================
    # AUTH
    # =========================
    path("signup/", views.signup, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="events:event_feed"), name="logout"),

    # =========================
    # CLUB SYSTEM
    # =========================

    # request to join a club (student side)
    path("clubs/join/<int:club_id>/", views.request_join_club, name="request_join_club"),

    # club admin view (pending requests for a club)
    path("clubs/<int:club_id>/requests/", views.club_requests, name="club_requests"),

    # approve / reject specific membership request
    path("clubs/membership/approve/<int:membership_id>/", views.approve_membership, name="approve_membership"),
    path("clubs/membership/reject/<int:membership_id>/", views.reject_membership, name="reject_membership"),
]