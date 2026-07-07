from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class InformatiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.informatique'
    verbose_name = _('Informatique')
