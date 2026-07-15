from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GestionDocumentaireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gestion_documentaire'
    verbose_name = _('Gestion documentaire')
