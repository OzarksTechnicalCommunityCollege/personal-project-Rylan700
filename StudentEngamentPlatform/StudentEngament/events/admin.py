from .models import Event

from django.contrib import admin

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "club", "status", "start_time")
    list_filter = ("status", "needs_facilities", "needs_IT", "needs_finance")
    search_fields = ("title", "description")