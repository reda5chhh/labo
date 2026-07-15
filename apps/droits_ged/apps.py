from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class DroitsGedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.droits_ged'
    verbose_name = _("Droits d'accès GED")
