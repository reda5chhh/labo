from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EspaceUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.espace_user'
    verbose_name = _('Espace Utilisateur')
