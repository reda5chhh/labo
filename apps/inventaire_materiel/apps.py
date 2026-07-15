from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class InventaireMaterielConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventaire_materiel'
    verbose_name = _('Inventaire Matériel')
