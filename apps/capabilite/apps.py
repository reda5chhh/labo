from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CapabiliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.capabilite'
    verbose_name = _('Capabilité')
