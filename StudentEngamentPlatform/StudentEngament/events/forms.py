from django import forms
from .models import Event, EventRegistration, SurveyResponse


# =========================
# EVENT CREATION FORM
# =========================
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "location",
            "start_time",
            "end_time",
            "expected_attendance",
            "needs_facilities",
            "needs_IT",
            "needs_finance",
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={"class": "form-control"}),

            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),

            "expected_attendance": forms.NumberInput(attrs={"class": "form-control"}),

            "needs_facilities": forms.CheckboxInput(),
            "needs_IT": forms.CheckboxInput(),
            "needs_finance": forms.CheckboxInput(),
        }


# =========================
# EVENT REGISTRATION FORM
# =========================
class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = []  # no input needed, it's system-driven


# =========================
# SURVEY RESPONSE FORM
# =========================
class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = ["rating", "feedback"]

        widgets = {
            "rating": forms.NumberInput(attrs={
                "min": 1,
                "max": 5,
                "class": "form-control"
            }),
            "feedback": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Optional feedback..."
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating