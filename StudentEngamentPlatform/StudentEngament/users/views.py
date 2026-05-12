import json

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncDate
from events.models import Event, Attendance, SurveyResponse
from points.models import PointTransaction
from .decorators import club_admin_required
from .models import UserBadge, Club, ClubMembership
from events.models import Attendance, EventRegistration 
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.utils import timezone
from django.contrib.auth.views import LoginView


User = get_user_model()

# =========================
# USER PROFILE
# =========================
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    clubs = Club.objects.all()

    memberships = {
        m.club_id: m.status
        for m in user.club_memberships.all()
    }

    primary_club = Club.objects.filter(admin=user).first()

    if not primary_club:
        membership = user.club_memberships.filter(status="approved").select_related("club").first()
        primary_club = membership.club if membership else None

    return render(request, "users/profile.html", {
        "user_obj": user,
        "clubs": clubs,
        "memberships": memberships,
        "primary_club": primary_club,
    })


# =========================
# USER BADGES
# =========================
def user_badges(request, user_id):
    """
    Returns all badges owned by a user.
    """

    user = get_object_or_404(User, id=user_id)

    badges = UserBadge.objects.filter(user=user).select_related("badge")

    return render(request, "points/badges.html", {
        "user_obj": user,
        "user_badges": badges
    })


# =========================
# USER ACTIVITY OVERVIEW
# =========================
def user_activity(request, user_id):
    """
    Combined snapshot of user engagement:
    - attendance
    - registrations
    - badges
    """

    user = get_object_or_404(User, id=user_id)

    return render(request, "users/activity.html", {
        "user_obj": user,
        "attendance": Attendance.objects.filter(student=user).count(),
        "registrations": EventRegistration.objects.filter(user=user).count(),
        "badges": UserBadge.objects.filter(user=user).count(),
    })


# =========================
# Signup View
# =========================
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after signup
            return redirect("users:user_profile", user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})


# =========================
# Custom Login View
# =========================
class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        user = self.request.user
        return f"/users/profile/{user.id}/"


# =========================
# Join Club View
# =========================
def request_join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user = request.user

    # =========================
    # ADMIN AUTO-APPROVAL
    # =========================
    if club.admin == user:
        ClubMembership.objects.get_or_create(
            user=user,
            club=club,
            defaults={
                "status": "approved",
                "approved_at": timezone.now()
            }
        )
        return redirect("users:user_profile", user_id=user.id)

    # =========================
    # NORMAL USER FLOW
    # =========================
    membership, created = ClubMembership.objects.get_or_create(
        user=user,
        club=club
    )

    if created:
        membership.status = "pending"
        membership.save()

    return redirect("users:user_profile", user_id=user.id)


@club_admin_required
# =========================
# Club Requests View
# =========================
def club_requests(request, club_id):
    club = get_object_or_404(Club, id=club_id)

    # safety check
    if request.user != club.admin:
        return redirect("users:user_profile", user_id=request.user.id)

    requests = ClubMembership.objects.filter(
        club=club,
        status="pending"
    ).select_related("user")

    return render(request, "users/club_requests.html", {
        "club": club,
        "requests": requests
    })

@club_admin_required
# =========================
# Approve Club Membership View
# =========================
def approve_membership(request, membership_id):
    membership = get_object_or_404(ClubMembership, id=membership_id)

    # safety check: only club admin can approve
    if request.user != membership.club.admin:
        return redirect("users:user_profile", user_id=request.user.id)

    membership.status = "approved"
    membership.approved_at = timezone.now()
    membership.save()

    return redirect("users:club_requests", club_id=membership.club.id)


@club_admin_required
# =========================
# Reject Club Membership View
# =========================
def reject_membership(request, membership_id):
    membership = get_object_or_404(ClubMembership, id=membership_id)

    if request.user != membership.club.admin:
        return redirect("users:user_profile", user_id=request.user.id)

    membership.status = "rejected"
    membership.save()

    return redirect("users:club_requests", club_id=membership.club.id)

# =========================
# Get a list of all members in a club (for admin view)
# =========================
@club_admin_required
def club_members_api(request, club_id):

    club = get_object_or_404(Club, id=club_id)

    members = ClubMembership.objects.filter(
        club=club,
        status="approved"
    ).select_related("user")

    data = []

    for member in members:
        data.append({
            "id": member.user.id,
            "username": member.user.username,
            "joined": member.approved_at
        })

    return JsonResponse(data, safe=False)

# =========================
# CLUB MEMBERS PAGE
# =========================
@club_admin_required
def club_members_page(request, club_id):

    club = get_object_or_404(Club, id=club_id)

    # security check
    if request.user != club.admin:
        return redirect("users:user_profile", user_id=request.user.id)

    members = ClubMembership.objects.filter(
        club=club,
        status="approved"
    ).select_related("user")

    return render(request, "users/club_members.html", {
        "club": club,
        "members": members
    })


# =========================
# Club Dashboard View
# =========================
@club_admin_required
def club_dashboard(request):

    club = Club.objects.filter(admin=request.user).first()

    if not club:
        return redirect("events:event_feed")

    # =========================
    # BASIC COUNTS
    # =========================
    total_members = ClubMembership.objects.filter(
        club=club,
        status="approved"
    ).count()

    pending_requests = ClubMembership.objects.filter(
        club=club,
        status="pending"
    ).count()

    total_events = Event.objects.filter(
        club=club
    ).count()

    total_attendance = Attendance.objects.filter(
        event__club=club
    ).count()

    # =========================
    # ATTENDANCE BY EVENT
    # =========================
    attendance_by_event = (
        Attendance.objects
        .filter(event__club=club)
        .values("event__title")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # =========================
    # DAILY CHECK-INS
    # =========================
    daily_attendance = (
        Attendance.objects
        .filter(event__club=club)
        .annotate(day=TruncDate("checked_in_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # =========================
    # SURVEY RATINGS
    # =========================
    survey_ratings = (
        SurveyResponse.objects
        .filter(survey__event__club=club)
        .values("survey__event__title")
        .annotate(avg_rating=Avg("rating"))
        .order_by("-avg_rating")
    )

    # =========================
    # CLUB POINTS
    # =========================
    points_over_time = (
        PointTransaction.objects
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("leaderboard_points"))
        .order_by("day")
    )

    context = {

        # =========================
        # CLUB INFO
        # =========================
        "club": club,
        "total_members": total_members,
        "pending_requests": pending_requests,
        "total_events": total_events,
        "total_attendance": total_attendance,

        # =========================
        # CHART DATA
        # =========================
        "attendance_labels": json.dumps([
            item["event__title"]
            for item in attendance_by_event
        ]),

        "attendance_data": json.dumps([
            item["total"]
            for item in attendance_by_event
        ]),

        "daily_labels": json.dumps([
            str(item["day"])
            for item in daily_attendance
        ]),

        "daily_data": json.dumps([
            item["total"]
            for item in daily_attendance
        ]),

        "survey_labels": json.dumps([
            item["survey__event__title"]
            for item in survey_ratings
        ]),

        "survey_data": json.dumps([
            float(item["avg_rating"])
            for item in survey_ratings
        ]),

        "points_labels": json.dumps([
            str(item["day"])
            for item in points_over_time
        ]),

        "points_data": json.dumps([
            item["total"] or 0
            for item in points_over_time
        ]),
    }

    return render(request, "users/club_dashboard.html", context)