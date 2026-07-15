from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FicheVieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fiche_vie'
    verbose_name = _('Fiche de vie')
