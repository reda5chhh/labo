from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class FormationQualificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.formation_qualification'
    verbose_name = _('Formation et Qualification')
