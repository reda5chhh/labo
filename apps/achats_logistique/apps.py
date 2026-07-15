from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AchatsLogistiqueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.achats_logistique'
    verbose_name = _('Achats et Logistique')
