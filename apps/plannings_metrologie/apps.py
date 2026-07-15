from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class PlanningsMetrologieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.plannings_metrologie'
    verbose_name = _('Plannings Métrologie')
