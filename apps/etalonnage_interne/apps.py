from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EtalonnageInterneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.etalonnage_interne'
    verbose_name = _('Étalonnage interne')
