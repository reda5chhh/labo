from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MarchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marches'
    verbose_name = _('Marchés')
