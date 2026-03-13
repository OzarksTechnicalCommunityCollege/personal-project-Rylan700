from django.contrib import admin
from .models import SpeedRun, Category

# Register the SpeedRun model in Django admin
@admin.register(SpeedRun)
class SpeedRunAdmin(admin.ModelAdmin):
    list_display = ['game', 'player', 'hours', 'minutes', 'seconds', 'milliseconds', 'verified', 'submit_time']
    list_filter = ['verified', 'submit_time']  # Filter options in sidebar
    search_fields = ['player__username']       # Search by player's username
    raw_id_fields = ['player']                 # Show user as raw ID instead of dropdown
    ordering = ['hours', 'minutes', 'seconds', 'milliseconds']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Auto-fill slug from name
    search_fields = ['name']