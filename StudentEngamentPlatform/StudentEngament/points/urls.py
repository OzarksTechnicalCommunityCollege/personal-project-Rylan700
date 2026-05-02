from django.urls import path
from . import views

app_name = "points"

urlpatterns = [

    # =========================
    # CORE POINTS
    # =========================
    path('balance/<int:user_id>/', views.user_balance, name="balance"),
    path('add/', views.add_points, name="add_points"),

    # =========================
    # LEADERBOARD
    # =========================
    path('leaderboard/', views.leaderboard_page, name='leaderboard'),

    # =========================
    # SHOP SYSTEM
    # =========================
    path('shop/', views.shop_page, name="shop"),

    # FIXED: no item_id in URL anymore
    path('purchase/', views.purchase_item, name="purchase_item"),

    # =========================
    # BADGE ADMIN
    # =========================
    path('badges/admin/', views.badge_admin_page, name="badge_admin"),

    # =========================
    # VOUCHER ADMIN
    # =========================
    path("vouchers/admin/", views.voucher_admin_page, name="voucher_admin"),
]