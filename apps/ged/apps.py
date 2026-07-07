from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class GedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ged'
    verbose_name = _('GED — Gestion Électronique de Documents')
