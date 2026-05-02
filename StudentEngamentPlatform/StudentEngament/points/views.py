from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from .forms import BadgeForm

from .models import (
    PointTransaction,
    Purchase,
    Badge,
    UserBadge,
    Voucher,
    UserVoucher
)

from events.models import Attendance

User = get_user_model()


# =========================
# UTILITY: BALANCE CALCULATOR
# =========================
def get_shop_balance(user):
    """
    RETURNS CURRENT SPENDABLE SHOP POINTS
    """

    return PointTransaction.objects.filter(user=user).aggregate(
        shop=Sum("shop_points")
    )["shop"] or 0


def get_leaderboard_score(user):
    """
    RETURNS NON-SPENDABLE LEADERBOARD SCORE
    """

    return PointTransaction.objects.filter(user=user).aggregate(
        leaderboard=Sum("leaderboard_points")
    )["leaderboard"] or 0


# =========================
# USER BALANCE API
# =========================
def user_balance(request, user_id):
    """
    RETURNS BOTH POINT TYPES
    """

    totals = PointTransaction.objects.filter(user_id=user_id).aggregate(
        leaderboard=Sum("leaderboard_points"),
        shop=Sum("shop_points")
    )

    return JsonResponse({
        "leaderboard_points": totals["leaderboard"] or 0,
        "shop_points": totals["shop"] or 0
    })


# =========================
# ADD POINTS (GLOBAL SYSTEM)
# =========================
@require_POST
def add_points(request):
    """
    CENTRAL POINT LEDGER ENTRY
    """

    user_id = request.POST.get("user_id")

    if not user_id:
        return JsonResponse({"error": "user_id is required"}, status=400)

    user = get_object_or_404(User, id=user_id)

    try:
        leaderboard_points = int(request.POST.get("leaderboard_points", 0))
        shop_points = int(request.POST.get("shop_points", 0))
    except ValueError:
        return JsonResponse({"error": "Points must be integers"}, status=400)

    PointTransaction.objects.create(
        user=user,
        leaderboard_points=leaderboard_points,
        shop_points=shop_points,
        reason=request.POST.get("reason", "manual award"),
        source_type=request.POST.get("source_type"),
        source_id=request.POST.get("source_id")
    )

    # IMPORTANT: check automatic badges after points/events
    check_automatic_badges(user)

    return JsonResponse({"message": "points added"})


# =========================
# LEADERBOARD PAGE
# =========================
def leaderboard_page(request):
    """
    RANK USERS BY LEADERBOARD SCORE
    """

    leaderboard = (
        User.objects
        .annotate(score=Sum("point_transactions__leaderboard_points"))
        .order_by("-score")
    )

    return render(request, "points/leaderboard.html", {
        "leaderboard": leaderboard
    })


# =========================
# SHOP PAGE
# =========================
@login_required
def shop_page(request):

    badges = Badge.objects.filter(
        acquisition_type="shop",
        shop_price__isnull=False
    )

    vouchers = Voucher.objects.filter(is_active=True)

    return render(request, "points/shop.html", {
        "badges": badges,
        "vouchers": vouchers,
        "shop_points": get_shop_balance(request.user)
    })


# =========================
# PURCHASE ITEM
# =========================
@require_POST
@login_required
def purchase_item(request):

    user = request.user
    item_type = request.POST.get("item_type")
    item_id = request.POST.get("item_id")

    # =========================
    # BADGE PURCHASE
    # =========================
    if item_type == "badge":

        badge = get_object_or_404(Badge, id=item_id)

        if badge.acquisition_type != "shop":
            return JsonResponse({"error": "Not purchasable"}, status=400)

        price = badge.shop_price or 0

        if get_shop_balance(user) < price:
            return JsonResponse({"error": "Not enough points"}, status=400)

        PointTransaction.objects.create(
            user=user,
            shop_points=-price,
            reason=f"Purchased badge {badge.name}"
        )

        UserBadge.objects.get_or_create(user=user, badge=badge)

        return JsonResponse({"message": "badge purchased"})

    # =========================
    # VOUCHER PURCHASE
    # =========================
    elif item_type == "voucher":

        voucher = get_object_or_404(Voucher, id=item_id)

        if not voucher.is_active:
            return JsonResponse({"error": "Inactive voucher"}, status=400)

        if get_shop_balance(user) < voucher.cost:
            return JsonResponse({"error": "Not enough points"}, status=400)

        PointTransaction.objects.create(
            user=user,
            shop_points=-voucher.cost,
            reason=f"Purchased voucher {voucher.name}"
        )

        UserVoucher.objects.get_or_create(user=user, voucher=voucher)

        return JsonResponse({"message": "voucher purchased"})

    return JsonResponse({"error": "Invalid item type"}, status=400)


# =========================
# AUTOMATIC BADGE SYSTEM
# =========================
def check_automatic_badges(user):
    """
    GRANTS BADGES BASED ON EVENT ATTENDANCE
    """

    event_count = Attendance.objects.filter(student=user).count()

    auto_badges = Badge.objects.filter(acquisition_type="automatic")

    for badge in auto_badges:
        if badge.required_events and event_count >= badge.required_events:

            UserBadge.objects.get_or_create(
                user=user,
                badge=badge
            )


# =========================
# BADGE ADMIN PAGE
# =========================
@login_required
def badge_admin_page(request):
    """
    ADMIN BADGE MANAGEMENT
    """

    if request.user.role != "club_admin":
        return JsonResponse({"error": "Not authorized"}, status=403)

    if request.method == "POST":
        form = BadgeForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("points:badge_admin")

    else:
        form = BadgeForm()

    badges = Badge.objects.all()
    user_badges = UserBadge.objects.select_related("user", "badge")

    return render(request, "points/badge_admin.html", {
        "form": form,
        "badges": badges,
        "user_badges": user_badges
    })



# =========================
# Voucher Redemption
# =========================
@login_required
@require_POST
def redeem_voucher(request, voucher_id):
    """
    USE A VOUCHER
    """

    user = request.user
    user_voucher = get_object_or_404(UserVoucher, id=voucher_id, user=user)

    if user_voucher.redeemed:
        return JsonResponse({"error": "Already used"}, status=400)

    voucher = user_voucher.voucher

    # =========================
    # APPLY EFFECTS
    # =========================
    if voucher.voucher_type == "extra_credit":
        PointTransaction.objects.create(
            user=user,
            leaderboard_points=voucher.value,
            reason="Extra Credit Voucher"
        )

    elif voucher.voucher_type == "multiplier":
        # (you can later hook this into event logic)
        pass

    elif voucher.voucher_type == "extension":
        # (hook into assignment system later)
        pass

    user_voucher.redeemed = True
    user_voucher.redeemed_at = timezone.now()
    user_voucher.save()

    return JsonResponse({"message": "voucher redeemed"})
    


# =========================
# VOUCHER ADMIN PAGE
# =========================
@login_required
def voucher_admin_page(request):
    """
    ADMIN ONLY VOUCHER CONTROL PANEL
    """

    if request.user.role != "club_admin":
        return JsonResponse({"error": "Not authorized"}, status=403)

    # =========================
    # CREATE VOUCHER
    # =========================
    if request.method == "POST":
        Voucher.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description", ""),
            cost=request.POST.get("cost"),
            voucher_type=request.POST.get("voucher_type"),
            value=request.POST.get("value", 1),
        )

        return redirect("points:voucher_admin")

    vouchers = Voucher.objects.all()
    user_vouchers = UserVoucher.objects.select_related("user", "voucher")

    return render(request, "points/voucher_admin.html", {
        "vouchers": vouchers,
        "user_vouchers": user_vouchers
    })