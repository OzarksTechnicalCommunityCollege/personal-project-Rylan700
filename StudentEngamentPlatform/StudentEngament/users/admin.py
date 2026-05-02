from django.contrib import admin

from .models import Club, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role")
    search_fields = ("username", "email")

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
