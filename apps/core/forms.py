"""
LABO.COS App — Formulaires de l'application core.

- LaboCOSAuthenticationForm : formulaire de connexion Bootstrap 5 personnalisé.
- UserProfileForm : formulaire de mise à jour du profil utilisateur.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class LaboCOSAuthenticationForm(AuthenticationForm):
    """
    Formulaire de connexion personnalisé avec classes Bootstrap 5
    et messages d'erreurs localisés en français.
    """
    username = forms.CharField(
        label=_('Identifiant'),
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Votre identifiant'),
            'autofocus': True,
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label=_('Mot de passe'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Votre mot de passe'),
            'autocomplete': 'current-password',
        }),
    )

    error_messages = {
        'invalid_login': _(
            'Identifiant ou mot de passe incorrect. '
            'Attention, le mot de passe est sensible à la casse.'
        ),
        'inactive': _('Ce compte est désactivé. Contactez l\'administrateur.'),
    }


class UserProfileForm(forms.ModelForm):
    """
    Formulaire de mise à jour du profil utilisateur.
    Permet à l'utilisateur de modifier ses informations personnelles.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'fonction', 'signature_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'signature_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Email'),
            'fonction': _('Fonction'),
            'signature_image': _('Signature'),
        }


class UserAdminCreationForm(UserCreationForm):
    """Formulaire de création d'utilisateur pour l'interface d'administration."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('fonction', 'est_admin')
        widgets = {
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserAdminChangeForm(UserChangeForm):
    """Formulaire de modification d'utilisateur pour l'interface d'administration."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'
