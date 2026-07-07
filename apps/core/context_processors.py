"""
LABO.COS App — Context processors globaux.

Injecte les paramètres du laboratoire dans tous les templates.
"""
from django.conf import settings


def labo_settings(request):
    """
    Injecte les paramètres globaux du laboratoire dans le contexte
    de chaque template (nom, adresse, téléphone, etc.).
    """
    return {
        'LABO_NOM': getattr(settings, 'LABO_NOM', 'LABO.COS'),
        'LABO_ADRESSE': getattr(settings, 'LABO_ADRESSE', ''),
        'LABO_TEL': getattr(settings, 'LABO_TEL', ''),
        'LABO_EMAIL': getattr(settings, 'LABO_EMAIL', ''),
        'LABO_SITE': getattr(settings, 'LABO_SITE', ''),
    }
