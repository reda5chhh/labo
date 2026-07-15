from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TableReceptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.table_receptions'
    verbose_name = _('Table des réceptions')
