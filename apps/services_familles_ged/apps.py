from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ServicesFamillesGedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.services_familles_ged'
    verbose_name = _('Services/Familles GED')
