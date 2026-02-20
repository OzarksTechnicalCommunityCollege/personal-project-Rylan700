from django import forms
from .models import SpeedRun

# ========================
# Form for submitting a new speed run
# ========================
class SubmitRunForm(forms.ModelForm):
    class Meta:
        model = SpeedRun  # The model this form is based on
        fields = [
            'game',        # Name of the game
            'player',      # Player submitting the run
            'hours',       # Hours part of the run time
            'minutes',     # Minutes part of the run time
            'seconds',     # Seconds part of the run time
            'milliseconds',# Milliseconds part of the run time
            'video'        # File upload for proof of run
        ]