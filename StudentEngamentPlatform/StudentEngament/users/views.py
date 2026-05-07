from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
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