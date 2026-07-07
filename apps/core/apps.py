"""
LABO.COS App — Configuration de l'application core.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    """Configuration de l'application core."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = _('Noyau du système')

    def ready(self):
        """Importer les signaux quand l'app est prête."""
        import apps.core.signals  # noqa: F401
