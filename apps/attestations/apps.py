from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AttestationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.attestations'
    verbose_name = _('Attestations')
