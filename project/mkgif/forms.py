from django import forms
from mkgif.models import Animation, YouTubeVideo


FORMAT_CHOICES = [
    ("mp4", "mp4"),
    ("gif", "gif"),
    ("png", "png"),
]


class AnimationForm(forms.ModelForm):
    framerate = forms.IntegerField()
    scale = forms.IntegerField()
    select_type_from = forms.ChoiceField(
        required=False, widget=forms.Select, choices=FORMAT_CHOICES
    )
    select_type_to = forms.ChoiceField(
        required=False, widget=forms.Select, choices=FORMAT_CHOICES
    )

    class Meta:
        model = Animation
        fields = ("name",)


class YouTubeDownloadForm(forms.Form):
    youtube_url = forms.URLField(label="YouTube URL", required=True)
    start_time = forms.CharField(label="Start Time (HH:MM:SS)", required=True)
    end_time = forms.CharField(label="End Time (HH:MM:SS)", required=True)
    video_name = forms.CharField(label="Video name", required=True)



class MusicDownloadForm(forms.Form):
    music_file_name = forms.CharField(label="Music name", required=True)
    music_file = forms.FileField(label="Upload MP4 File", required=True)
