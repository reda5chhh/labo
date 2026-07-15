from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MajIncertitudeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.maj_incertitude'
    verbose_name = _('MAJ incertitude')
