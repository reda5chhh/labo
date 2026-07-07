from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TechniqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.technique'
    verbose_name = _('Technique')
