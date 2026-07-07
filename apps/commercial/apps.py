"""
LABO.COS App — Application Commercial.
Gère : Clients, Revue de Demande, Devis, Dossiers, Conventions,
AO, Cautions, Bons de Livraison.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommercialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.commercial'
    verbose_name = _('Commercial')
