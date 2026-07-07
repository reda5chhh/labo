"""
LABO.COS App — Configuration Celery
Initialise l'application Celery avec auto-découverte des tâches.
"""
import os
from celery import Celery

# Définir le module de settings Django par défaut pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labocos.settings.local')

app = Celery('labocos')

# Charger la configuration depuis les settings Django (préfixe CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications installées
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester la connexion Celery."""
    print(f'Request: {self.request!r}')
