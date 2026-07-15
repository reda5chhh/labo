from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ParametrageGeneralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.parametrage_general'
    verbose_name = _('Paramétrage Général')
