from django.utils import timezone

from django.db import models
from django.conf import settings


# =========================
# EVENT MODEL
# =========================
class Event(models.Model):
    """
    Core entity of the platform.

    Lifecycle:
    draft -> submitted -> approved -> published -> completed

    Handles:
    - event creation
    - approval routing
    - attendance tracking (via Attendance model)
    """

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('completed', 'Completed'),
    ]

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def is_completed(self):
        now = timezone.now()
        return now > self.end_time

    # Relationships
    club = models.ForeignKey('users.Club', on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events"
        
    )

    # event details
    title = models.CharField(max_length=200)
    description = models.TextField()

    location = models.CharField(max_length=200)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    expected_attendance = models.PositiveIntegerField(default=0)

    # resource routing flags
    needs_facilities = models.BooleanField(default=False)
    needs_IT = models.BooleanField(default=False)
    needs_finance = models.BooleanField(default=False)

    # workflow state
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================
# Event Registration Model
# =========================
class EventRegistration(models.Model):
    """
    Represents a student signing up for an event.
    Part of event lifecycle BEFORE attendance.
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE
    )

    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} -> {self.event.title}"

# =========================
# ATTENDANCE (QR CHECK-IN SYSTEM)
# =========================
class Attendance(models.Model):
    """
    Tracks student attendance for events.

    This is the SINGLE source of truth for:
    - check-in system
    - participation tracking
    - feeding points system (external app)
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    student = models.ForeignKey('users.User', on_delete=models.CASCADE)

    checked_in = models.BooleanField(default=True)

    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.event.title}"


# =========================
# SURVEY SYSTEM
# =========================
class Survey(models.Model):
    """
    Post-event feedback form.
    """

    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    title = models.CharField(max_length=200, default="Event Feedback")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Survey for {self.event.title}"


# =========================
# SURVEY RESPONSES
# =========================
class SurveyResponse(models.Model):
    """
    Stores student feedback per event.
    Used for analytics + gamification rewards.
    """

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField()  # 1–5 scale
    feedback = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('survey', 'student')

    def __str__(self):
        return f"{self.student.username} response"