from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CongesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.conges'
    verbose_name = _('Congé')
