"""Configuration de l'administration Django pour le module technique."""
from django.contrib import admin
from .models import Reception


@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('num_reception', 'client', 'date_reception', 'nature_echantillon', 'etat_essai', 'etat_rapport', 'facture')
    list_filter = ('etat_essai', 'etat_rapport', 'date_reception', 'nature_echantillon')
    search_fields = ('num_reception', 'client__nom', 'dossier__reference')
    date_hierarchy = 'date_reception'
