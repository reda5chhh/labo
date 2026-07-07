from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AchatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.achats'
    verbose_name = _('Achats')
