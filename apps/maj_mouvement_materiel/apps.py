from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MajMouvementMaterielConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.maj_mouvement_materiel'
    verbose_name = _('Gestion mouvement Matériel')
