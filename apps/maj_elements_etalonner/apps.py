from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MajElementsEtalonnerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.maj_elements_etalonner'
    verbose_name = _('MAJ éléments à étalonner')
