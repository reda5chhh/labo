"""
LABO.COS App — Formulaires du service technique.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Reception


class ReceptionForm(forms.ModelForm):
    class Meta:
        model = Reception
        fields = [
            'num_reception', 'client', 'dossier', 'date_reception',
            'nature_echantillon', 'etat_essai', 'etat_rapport',
            'charge_prelevement', 'facture', 'bordereau',
        ]
        widgets = {
            'num_reception': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'REC-2026-001'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'dossier': forms.Select(attrs={'class': 'form-select'}),
            'date_reception': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nature_echantillon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Béton, Sol, Eau…')}),
            'etat_essai': forms.Select(attrs={'class': 'form-select'}),
            'etat_rapport': forms.Select(attrs={'class': 'form-select'}),
            'charge_prelevement': forms.TextInput(attrs={'class': 'form-control'}),
            'facture': forms.Select(attrs={'class': 'form-select'}),
            'bordereau': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'BE-2026-001'}),
        }
        labels = {
            'num_reception': _('N° Réception'),
            'client': _('Client'),
            'dossier': _('Dossier'),
            'date_reception': _('Date de réception'),
            'nature_echantillon': _("Nature de l'échantillon"),
            'etat_essai': _("État de l'essai"),
            'etat_rapport': _('État du rapport'),
            'charge_prelevement': _('Chargé de prélèvement'),
            'facture': _('Facture liée'),
            'bordereau': _("N° Bordereau d'envoi"),
        }
