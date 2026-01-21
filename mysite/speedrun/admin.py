from django.contrib import admin
from .models import SpeedRun

# Register your models here.
@admin.register(SpeedRun)
class SpeedRunAdmin(admin.ModelAdmin):
    list_display = ['player', 'hours', 'minutes', 'seconds', 'milliseconds', 'verified', 'submit_time']
    list_filter = ['verified', 'submit_time']
    search_fields = ['player__username']
    raw_id_fields = ['player']
    ordering = ['-hours', '-minutes', '-seconds', '-milliseconds']
    show_facets = admin.ShowFacets.ALWAYS