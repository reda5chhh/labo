from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class QualiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.qualite'
    verbose_name = _('Qualité')
