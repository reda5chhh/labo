from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MetrologieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.metrologie'
    verbose_name = _('Métrologie')
