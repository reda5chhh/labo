from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FacturationComptabiliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.facturation_comptabilite'
    verbose_name = _('Facturation et Comptabilité')
