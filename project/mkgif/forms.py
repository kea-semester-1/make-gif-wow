from django import forms
from mkgif.models import Animation


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
