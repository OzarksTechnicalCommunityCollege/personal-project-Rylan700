from django.utils  import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


# =========================
# CUSTOM USER MODEL
# =========================
class User(AbstractUser):
    """
    Core user model for the Student Engagement Platform.

    Supports:
    - Role-based access control (student, club_admin, staff)
    - Integration with Events app (attendance, registration)
    - Integration with Points app (via external service)
    - Badge ownership (through UserBadge table)
    """

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('club_admin', 'Club Admin'),
        ('staff', 'Staff'),
    ]

    # Role determines permissions + UI access
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student'
    )

    def __str__(self):
        return self.username


# =========================
# CLUB MODEL
# =========================
class Club(models.Model):
    """
    Represents a student organization.

    Events belong to clubs.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_clubs"
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Ensure admin is always an approved member
        if self.admin:
            membership, created = ClubMembership.objects.get_or_create(
                user=self.admin,
                club=self,
                defaults={
                    "status": "approved",
                    "approved_at": timezone.now()
                }
            )

            # If membership existed but wasn't approved → fix it
            if not created and membership.status != "approved":
                membership.status = "approved"
                membership.approved_at = timezone.now()
                membership.save()

            # force role
            if self.admin.role != "club_admin":
                self.admin.role = "club_admin"
                self.admin.save()

    def __str__(self):
        return self.name


# =========================
# CLUB MEMBERSHIP MODEL
# =========================
class ClubMembership(models.Model):
    """
    Represents a user's relationship with a club.
    Handles:
    - join requests
    - approvals
    - multiple club memberships
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="club_memberships")
    club = models.ForeignKey('users.Club', on_delete=models.CASCADE, related_name="memberships")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    requested_at = models.DateTimeField(auto_now_add=True)

    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.status})"



# =========================
# BADGE MODEL
# =========================
class Badge(models.Model):
    """
    Defines available badges in the system.
    """

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    icon = models.ImageField(upload_to="badges/", blank=True, null=True)

    def __str__(self):
        return self.name


# =========================
# USER BADGE OWNERSHIP
# =========================
class UserBadge(models.Model):
    """
    Many-to-many relationship between users and badges.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="badges"
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )

    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"