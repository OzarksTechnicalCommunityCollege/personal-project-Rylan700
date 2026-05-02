from datetime import timedelta

from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, render, redirect
from users.models import Club
from users.decorators import club_admin_required
from .models import Event, Attendance, EventRegistration, Survey, SurveyResponse
from points.models import PointTransaction
from .forms import EventForm
from django.db.models import Q
from django.contrib import messages

User = get_user_model()


# =========================
# STUDENT EVENT FEED
# =========================
def event_feed(request):
    """
    All published + recent completed events students can browse.
    """

    update_event_statuses()

    now = timezone.now()
    one_week_ago = now - timedelta(days=7)

    # =========================
    # EVENTS
    # =========================
    events = Event.objects.filter(
        Q(status="published") |
        Q(status="completed", end_time__gte=one_week_ago)
    ).select_related("club").order_by("-start_time")

    # =========================
    # USER STATE MAPS
    # =========================
    attended_events = set(
        Attendance.objects.filter(student=request.user)
        .values_list("event_id", flat=True)
    )

    submitted_surveys = set(
        SurveyResponse.objects.filter(student=request.user)
        .values_list("survey__event_id", flat=True)
    )

    surveys = {
        s.event_id: s for s in Survey.objects.all()
    }

    # =========================
    # BUILD CONTEXT OBJECTS
    # =========================
    event_cards = []

    for event in events:
        event_cards.append({
            "event": event,
            "can_check_in": event.is_active(),
            "survey": surveys.get(event.id),
            "attended": event.id in attended_events,
            "survey_done": event.id in submitted_surveys,
        })

    return render(request, "events/event_feed.html", {
        "event_cards": event_cards
    })


# =========================
# CREATE EVENT (CLUB ADMIN)
# =========================
@club_admin_required
def create_event(request):
    """
    Draft event creation.
    """

    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():

            # =========================
            # GET CLUB (admin OR membership)
            # =========================
            club = Club.objects.filter(admin=request.user).first()

            if not club:
                membership = request.user.club_memberships.filter(status="approved").first()

                if not membership:
                    return redirect("events:event_feed")

                club = membership.club

            # =========================
            # CREATE EVENT
            # =========================
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.status = "draft"
            event.save()

            return redirect("events:event_feed")

    else:
        form = EventForm()

    return render(request, "events/create_event.html", {"form": form})


# =========================
# SUBMIT EVENT (ROUTING START)
# =========================
def submit_event(request, event_id):
    """
    Sends event into approval pipeline.
    """

    event = get_object_or_404(Event, id=event_id)
    event.status = "submitted"
    event.save()

    return redirect("events:event_feed")


# =========================
# REGISTER FOR EVENT
# =========================
def register_event(request, event_id):
    """
    Student registration.
    """

    event = get_object_or_404(Event, id=event_id)

    EventRegistration.objects.get_or_create(
        user=request.user,
        event=event
    )

    return redirect("events:event_feed")


# =========================
# CHECK-IN (QR OR MANUAL)
# =========================
def check_in(request, event_id):
    from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

def check_in(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    now = timezone.now()

    if not (event.start_time <= now <= event.end_time):
        messages.error(request, "Check-in only allowed during the event.")
        return redirect("events:event_feed")

    attendance, created = Attendance.objects.get_or_create(
        student=request.user,
        event=event
    )

    if created:
        PointTransaction.objects.create(
            user=request.user,
            leaderboard_points=15,
            shop_points=15,
            reason=f"Event attendance: {event.id}",
            source_type="event",
            source_id=str(event.id)
        )

        messages.success(request, "You successfully checked in!")

    else:
        messages.info(request, "You are already checked in.")

    return redirect("events:event_feed")


# =========================
# EVENT ATTENDANCE LIST
# =========================
def attendance_list(request, event_id):
    """
    Who attended this event.
    """

    attendance = Attendance.objects.filter(event_id=event_id).select_related("student")

    return render(request, "events/attendance_list.html", {
        "attendance": attendance
    })


# =========================
#  UPDATE EVENT STATUSES
# =========================
def update_event_statuses():
    now = timezone.now()

    # =========================
    # AUTO COMPLETE EVENTS
    # =========================
    Event.objects.filter(
        status="published",
        end_time__lt=now
    ).update(status="completed")


# =========================
#  SUBMIT SURVEY
# =========================
def submit_survey(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    event = survey.event

    now = timezone.now()

    # =========================
    # ONLY AFTER EVENT ENDS
    # =========================
    if now <= event.end_time:
        return HttpResponse("Survey only available after event ends.")

    # =========================
    # MUST HAVE ATTENDED
    # =========================
    attended = Attendance.objects.filter(
        event=event,
        student=request.user
    ).exists()

    if not attended:
        return HttpResponse("You must attend the event to complete the survey.")

    # =========================
    # ONLY ONE SURVEY RESPONSE
    # =========================
    existing = SurveyResponse.objects.filter(
        survey=survey,
        student=request.user
    ).exists()

    if existing:
        return HttpResponse("You already submitted this survey.")

    # =========================
    # CREATE SURVEY RESPONSE
    # =========================
    rating = request.POST.get("rating")
    feedback = request.POST.get("feedback", "")

    if not rating:
        return HttpResponse("Rating is required.")

    SurveyResponse.objects.create(
        survey=survey,
        student=request.user,
        rating=rating,
        feedback=feedback
    )

    # =========================
    # GIVE POINTS
    # =========================
    already_rewarded = PointTransaction.objects.filter(
        user=request.user,
        reason=f"Survey completion: {event.id}"
    ).exists()

    if not already_rewarded:
        PointTransaction.objects.create(
            user=request.user,
            leaderboard_points=30,
            shop_points=30,
            reason=f"Event attendance: {event.id}",
            source_type="event",
            source_id=str(event.id)
        )

    return redirect("events:event_feed")