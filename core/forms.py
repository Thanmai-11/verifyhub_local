from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Artifact


# ─────────────────────────────────────────────
#  Registration Form
# ─────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(
                                 attrs={'class': 'form-control',
                                        'placeholder': 'Email'}))

    class Meta(UserCreationForm.Meta):
        model  = User
        fields = UserCreationForm.Meta.fields + ('email',)

    # Add Bootstrap class to every field automatically
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


# ─────────────────────────────────────────────
#  Upload Artifact Form
# ─────────────────────────────────────────────
class ArtifactForm(forms.ModelForm):
    class Meta:
        model  = Artifact
        fields = ['skill', 'title', 'file']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'e.g. My Django Blog Project'}),
            'file':  forms.FileInput(attrs={'class': 'form-control'}),
        }