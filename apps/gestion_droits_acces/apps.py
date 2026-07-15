from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GestionDroitsAccesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gestion_droits_acces'
    verbose_name = _("Gestion des droits d'accès")
