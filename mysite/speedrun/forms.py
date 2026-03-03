from django import forms
from .models import SpeedRun
from .models import Profile
from django.contrib.auth import get_user_model


# ========================
# Form for submitting a new speed run
# ========================
class SubmitRunForm(forms.ModelForm):
    class Meta:
        model = SpeedRun  # The model this form is based on
        fields = [
            'game',
            'hours',
            'minutes',
            'seconds',
            'milliseconds',
            'video'
        ]
        
    def clean_video(self):
        video = self.cleaned_data.get('video')

        if not video:
            return video

        valid_extensions = ['mp4', 'mp3']
        extension = video.name.rsplit('.', 1)[-1].lower()

        if extension not in valid_extensions:
            raise forms.ValidationError(
                'Only MP3 or MP4 files are allowed.'
            )

        return video

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'email']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']