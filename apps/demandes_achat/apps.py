from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DemandesAchatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.demandes_achat'
    verbose_name = _('Demande Achat')
