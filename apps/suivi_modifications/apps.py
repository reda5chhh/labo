from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SuiviModificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.suivi_modifications'
    verbose_name = _('Suivi des modifications')
