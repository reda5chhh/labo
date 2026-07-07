"""
LABO.COS App — Middleware de traçabilité.

AuditLogMiddleware : injecte les informations de la requête HTTP
(utilisateur, IP, user-agent) dans le contexte du thread local,
pour être utilisées par AuditableMixin lors des opérations CRUD.
"""
import threading
from apps.core.models import AuditLog

# Stockage thread-local pour partager les données de requête entre le
# middleware et les mixins des modèles sans passer par les paramètres.
_thread_locals = threading.local()


def get_current_request():
    """Retourne la requête HTTP du thread courant, ou None."""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Retourne l'utilisateur authentifié du thread courant, ou None."""
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    return None


def get_current_ip():
    """Extrait l'adresse IP réelle de la requête (gère les proxies)."""
    request = get_current_request()
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AuditLogMiddleware:
    """
    Middleware qui :
    1. Stocke la requête HTTP dans le thread local (pour AuditableMixin).
    2. Enregistre les événements de connexion/déconnexion Django dans AuditLog.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Injecter la requête dans le thread local
        _thread_locals.request = request

        # Capturer l'état d'authentification avant traitement
        was_authenticated = request.user.is_authenticated if hasattr(request, 'user') else False

        response = self.get_response(request)

        # Détecter une déconnexion (utilisateur était connecté, ne l'est plus)
        is_authenticated_now = request.user.is_authenticated if hasattr(request, 'user') else False
        if was_authenticated and not is_authenticated_now:
            # L'utilisateur vient de se déconnecter
            pass  # Le signal est géré dans core/signals.py

        # Nettoyer le thread local après la requête
        _thread_locals.request = None

        return response

    def process_exception(self, request, exception):
        """Nettoyer le thread local en cas d'exception."""
        _thread_locals.request = None
        return None
