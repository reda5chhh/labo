from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ParametrageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.parametrage'
    verbose_name = _('Paramétrage')
