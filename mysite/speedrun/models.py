from django.db import models
from django.conf import settings
from django import forms
from django.urls import reverse

# ========================
# Custom Managers
# ========================

# Custom manager to return only runs that are verified.
class VerifiedRunsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            verified=SpeedRun.Verified.VERIFIED
        )


# ========================
# Main Model
# ========================

class SpeedRun(models.Model):
    # Choices for verified status
    class Verified(models.TextChoices):
        VERIFIED = 'Y', 'Verified'
        NOTVERIFIED = 'N', 'Not Verified'

    # Game name
    game = models.CharField(max_length=200)

    # Time fields
    hours = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    seconds = models.PositiveIntegerField()
    milliseconds = models.PositiveIntegerField()

    # Timestamp fields
    submit_time = models.DateTimeField(auto_now_add=True)  # Set when run is created
    updated_time = models.DateTimeField(auto_now=True)     # Updated on each save

    # Video file upload
    video = models.FileField(upload_to='Videos/')

    # Player who submitted the run
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Link to Django's User model
        on_delete=models.CASCADE,  # Delete runs if user is deleted
        related_name='runs'         # Access via user.runs
    )

    # Verified status
    verified = models.CharField(
        max_length=1,
        choices=Verified.choices,
        default=Verified.NOTVERIFIED
    )

    # Managers
    objects = models.Manager()             # Default manager
    verified_runs = VerifiedRunsManager()  # Custom manager

    class Meta:
        ordering = ['hours', 'minutes', 'seconds', 'milliseconds']  # Default ordering

    def __str__(self):
        return f'{self.game} | {self.player} - {self.hours, self.minutes, self.seconds, self.milliseconds}'

    #Returns URL to view the detail of this speed run.
    def get_absolute_url(self):
        return reverse(
            'speedrun:run_detail',
            args=[
                self.game,
                self.player.username,
                self.id
            ],
        )

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d/',
        blank=True
    )
    def __str__(self):
        return f'Profile of {self.user.username}'
