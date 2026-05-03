from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Attendance, SurveyResponse
from points.models import PointTransaction
from points.views import check_automatic_badges


# =========================
# ATTENDANCE → POINTS + BADGES
# =========================
@receiver(post_save, sender=Attendance)
def handle_attendance_created(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.student
    event = instance.event

    # Prevent duplicate rewards
    already_rewarded = PointTransaction.objects.filter(
        user=user,
        source_type="event",
        source_id=str(event.id),
        reason__icontains="attendance"
    ).exists()

    if already_rewarded:
        return

    # Award points
    PointTransaction.objects.create(
        user=user,
        leaderboard_points=15,
        shop_points=15,
        reason=f"Event attendance: {event.id}",
        source_type="event",
        source_id=str(event.id)
    )

    # Check automatic badges
    check_automatic_badges(user)


# =========================
# SURVEY → POINTS
# =========================
@receiver(post_save, sender=SurveyResponse)
def handle_survey_submission(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.student
    event = instance.survey.event

    already_rewarded = PointTransaction.objects.filter(
        user=user,
        source_type="survey",
        source_id=str(event.id)
    ).exists()

    if already_rewarded:
        return

    PointTransaction.objects.create(
        user=user,
        leaderboard_points=30,
        shop_points=30,
        reason=f"Survey completion: {event.id}",
        source_type="survey",
        source_id=str(event.id)
    )