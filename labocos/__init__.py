"""
LABO.COS App — Package principal Django.
Initialise Celery au démarrage de l'application.
"""
# Ce fichier garantit que l'app Celery est chargée quand Django démarre,
# afin que les décorateurs @shared_task fonctionnent correctement.
from .celery import app as celery_app

__all__ = ('celery_app',)
