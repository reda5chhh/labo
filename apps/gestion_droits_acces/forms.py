"""
LABO.COS App — Formulaires de gestion des utilisateurs et droits d'accès.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from apps.core.models import User


class UserCreateForm(forms.ModelForm):
    """Formulaire de création d'un nouvel utilisateur."""
    password1 = forms.CharField(
        label=_('Mot de passe'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label=_('Confirmer le mot de passe'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'fonction', 'est_admin', 'is_active']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'fonction':   forms.TextInput(attrs={'class': 'form-control'}),
            'est_admin':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_('Les mots de passe ne correspondent pas.'))
        if p1:
            validate_password(p1)
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Formulaire de modification d'un utilisateur (mot de passe optionnel)."""
    new_password = forms.CharField(
        label=_('Nouveau mot de passe (laisser vide pour ne pas changer)'),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'fonction', 'est_admin', 'is_active']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'fonction':   forms.TextInput(attrs={'class': 'form-control'}),
            'est_admin':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pwd = self.cleaned_data.get('new_password')
        if new_pwd:
            user.set_password(new_pwd)
        if commit:
            user.save()
        return user
