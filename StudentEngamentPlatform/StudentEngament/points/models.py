from django.db import models
from django.conf import settings


# =========================
# POINT TRANSACTION MODEL
# =========================
class PointTransaction(models.Model):
    """
    CORE LEDGER SYSTEM
    Records all point changes with metadata for auditing and rollback."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions"
    )

    # =========================
    # POINT SYSTEMS
    # =========================
    leaderboard_points = models.IntegerField(default=0)
    shop_points = models.IntegerField(default=0)

    # =========================
    # METADATA
    # =========================
    reason = models.CharField(max_length=120)

    source_type = models.CharField(max_length=50, blank=True, null=True)
    source_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | L:{self.leaderboard_points} S:{self.shop_points}"


# =========================
# BADGE MODEL
# =========================
class Badge(models.Model):
    ACQUISITION_CHOICES = [
        ("shop", "Shop Purchase"),
        ("automatic", "Automatic Unlock"),
    ]

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="badges/", blank=True, null=True)

    acquisition_type = models.CharField(
        max_length=20,
        choices=ACQUISITION_CHOICES
    )

    shop_price = models.IntegerField(null=True, blank=True)
    required_events = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


# =========================
# USER BADGES
# =========================
class UserBadge(models.Model):
    """
    USER ↔ BADGE RELATIONSHIP
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_badges"
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name="user_badges"
    )

    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


# =========================
# VOUCHER MODEL
# =========================
class Voucher(models.Model):
    VOUCHER_TYPES = [
        ("extra_credit", "Extra Credit"),
        ("extension", "Deadline Extension"),
        ("multiplier", "Point Multiplier"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    cost = models.IntegerField()
    voucher_type = models.CharField(max_length=30, choices=VOUCHER_TYPES)
    value = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# =========================
# USER VOUCHERS
# =========================
class UserVoucher(models.Model):
    """
    USER OWNED REDEEMABLE ITEMS
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_vouchers"
    )

    voucher = models.ForeignKey(
        Voucher,
        on_delete=models.CASCADE,
        related_name="user_vouchers"
    )

    redeemed = models.BooleanField(default=False)

    purchased_at = models.DateTimeField(auto_now_add=True)

    redeemed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.voucher.name}"
    

# =========================
# PURCHASE MODEL
# =========================
class Purchase(models.Model):
    """
    LOG OF SHOP ACTIVITY (UNIFIED BADGE + VOUCHER)
    """

    ITEM_TYPES = [
        ("badge", "Badge"),
        ("voucher", "Voucher"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)

    badge = models.ForeignKey(
        Badge,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    voucher = models.ForeignKey(
        Voucher,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.item_type == "badge":
            return f"{self.user.username} → {self.badge.name}"
        return f"{self.user.username} → {self.voucher.name}"