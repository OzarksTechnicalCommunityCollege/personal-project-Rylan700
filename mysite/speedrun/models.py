from django.db import models
from django.conf import settings
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

    # Returns verified runs for a specific game
    def for_game(self, game_name):
        return self.get_queryset().filter(game=game_name)


# ========================
# Main Model
# ========================


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


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

    # Store total time in milliseconds for efficient sorting
    total_time = models.PositiveIntegerField(editable=False, null=True)

    # Timestamp fields
    submit_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    # Video file upload
    video = models.FileField(upload_to='Videos/')

    # Player who submitted the run
    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='runs'
    )

    # Speedrun Categories
    categories = models.ManyToManyField(
        Category,
        related_name='runs',
        blank=True
    )

    # Verified status
    verified = models.CharField(
        max_length=1,
        choices=Verified.choices,
        default=Verified.NOTVERIFIED
    )

    # Managers
    objects = models.Manager()
    verified_runs = VerifiedRunsManager()

    class Meta:
        # Order by computed total time instead of individual fields
        ordering = ['total_time']

    def __str__(self):
        # Clean readable format instead of tuple
        return f"{self.game} | {self.player} - {self.hours:02}:{self.minutes:02}:{self.seconds:02}.{self.milliseconds:03}"

    # ========================
    # Custom Behavior Methods
    # ========================

    # Converts time fields into total milliseconds
    def total_milliseconds(self):
        return (
            self.hours * 3600000 +
            self.minutes * 60000 +
            self.seconds * 1000 +
            self.milliseconds
        )

    # Override save to automatically calculate total_time
    def save(self, *args, **kwargs):
        # Ensure player exists before saving
        if not self.player_id:
            raise ValueError("SpeedRun must have a player")

        # Calculate total time before saving
        self.total_time = self.total_milliseconds()

        super().save(*args, **kwargs)

    # Returns URL to view the detail of this speed run.
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