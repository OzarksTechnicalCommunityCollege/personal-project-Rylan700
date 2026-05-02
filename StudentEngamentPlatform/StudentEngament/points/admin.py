from django.contrib import admin
from .models import (
    PointTransaction,
    Badge,
    UserBadge,
    Purchase,
    Voucher,
    UserVoucher
)


# =========================
# POINT TRANSACTIONS
# =========================
@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "leaderboard_points", "shop_points", "reason", "source_type", "created_at")
    list_filter = ("reason", "source_type", "created_at")
    search_fields = ("user__username", "reason", "source_id")
    ordering = ("-created_at",)


# =========================
# BADGES
# =========================
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "acquisition_type", "shop_price", "required_events")
    list_filter = ("acquisition_type",)
    search_fields = ("name",)


# =========================
# USER BADGES
# =========================
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "unlocked_at")
    list_filter = ("badge", "unlocked_at")
    search_fields = ("user__username", "badge__name")
    ordering = ("-unlocked_at",)


# =========================
# PURCHASES (SHOP LOG)
# =========================
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "item_type", "get_item", "created_at")
    search_fields = ("user__username",)
    list_filter = ("item_type",)

    def get_item(self, obj):
        if obj.item_type == "badge":
            return obj.badge
        return obj.voucher

    get_item.short_description = "Item"

# =========================
# VOUCHERS
# =========================
@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ("name", "voucher_type", "cost", "value", "is_active")
    list_filter = ("voucher_type", "is_active")
    search_fields = ("name",)
    ordering = ("name",)


# =========================
# USER VOUCHERS
# =========================
@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ("user", "voucher", "redeemed", "purchased_at", "redeemed_at")
    list_filter = ("redeemed", "voucher", "purchased_at")
    search_fields = ("user__username", "voucher__name")
    ordering = ("-purchased_at",)