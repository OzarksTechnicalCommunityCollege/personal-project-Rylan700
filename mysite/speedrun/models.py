from django.db import models
from django.utils import timezone
from django.conf import settings

# Create your models here.
class VerifiedRunsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            verified=SpeedRun.Verified.VERIFIED
        )


class SpeedRun(models.Model):

    class Verified(models.TextChoices):
        VERIFIED = 'Y', 'Verified'
        NOTVERIFIED = 'N', 'Not Verified'

    hours = models.PositiveIntegerField()
    minutes = models.PositiveIntegerField()
    seconds = models.PositiveIntegerField()
    milliseconds = models.PositiveIntegerField()
    submit_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='runs'
    )

    verified = models.CharField(
        max_length=2,
        choices=Verified.choices,
        default=Verified.NOTVERIFIED
    )

    objects = models.Manager()
    verified_runs = VerifiedRunsManager()

    class Meta:
        ordering = ['-hours', '-minutes', '-seconds', '-milliseconds']

    def __str__(self):
        return f'{self.player} - {self.speed_time}'
