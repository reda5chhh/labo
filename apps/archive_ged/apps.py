from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ArchiveGedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.archive_ged'
    verbose_name = _('Archive GED')
