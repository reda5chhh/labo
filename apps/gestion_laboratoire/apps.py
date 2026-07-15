from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GestionLaboratoireConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gestion_laboratoire'
    verbose_name = _('Gestion laboratoire')
