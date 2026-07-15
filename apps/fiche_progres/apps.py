from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FicheProgresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fiche_progres'
    verbose_name = _('Fiche de progrès')
