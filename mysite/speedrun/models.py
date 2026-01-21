from django.db import models
from django.conf import settings
from django import forms

# Custom manager to return only verified runs
class VerifiedRunsManager(models.Manager):
    def get_queryset(self):
        # Filter to only include runs marked as VERIFIED when queried
        return super().get_queryset().filter(
            verified=SpeedRun.Verified.VERIFIED
        )


class SpeedRun(models.Model):

    # Choices for verified status
    class Verified(models.TextChoices):
        VERIFIED = 'Y', 'Verified'
        NOTVERIFIED = 'N', 'Not Verified'

    # Time fields for the speed run 
    # might find a way to scan the video's time
    hours = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    seconds = models.PositiveIntegerField()
    milliseconds = models.PositiveIntegerField()
    
    # Timestamp fields
    submit_time = models.DateTimeField(auto_now_add=True)  # Set on creation
    updated_time = models.DateTimeField(auto_now=True)     # Updated on each save

    # Video file upload so that you can upload the video of the speedrun
    # Found on Django's documentation
    video = models.FileField(upload_to='Videos/')
    
    # Player who submitted the run
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Link to Django's user model
        on_delete=models.CASCADE,
        related_name='runs'        # Access from user.runs
    )

    # Verified status of the run
    verified = models.CharField(
        max_length=2,
        choices=Verified.choices,
        default=Verified.NOTVERIFIED
    )

    # Managers
    objects = models.Manager()            # Default manager
    verified_runs = VerifiedRunsManager()  # Custom manager for verified runs

    class Meta:
        # Default ordering for querysets
        ordering = ['-hours', '-minutes', '-seconds', '-milliseconds']

    # String for admin
    def __str__(self):
        return f'{self.player} - {self.hours, self.minutes, self.seconds, self.milliseconds}'
