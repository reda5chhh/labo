"""
LABO.COS App — Signaux Django pour l'application core.

Gère les événements globaux Django (connexion, déconnexion)
et les enregistre dans AuditLog.
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


def _get_client_ip(request):
    """Extrait l'IP du client depuis la requête."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Enregistre chaque connexion réussie dans AuditLog."""
    from apps.core.models import AuditLog
    AuditLog.log(
        user=user,
        action_type=AuditLog.ActionType.LOGIN,
        model_name='User',
        object_id=user.pk,
        object_repr=str(user),
        ip_address=_get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Enregistre chaque déconnexion dans AuditLog."""
    from apps.core.models import AuditLog
    if user:
        AuditLog.log(
            user=user,
            action_type=AuditLog.ActionType.LOGOUT,
            model_name='User',
            object_id=user.pk,
            object_repr=str(user),
            ip_address=_get_client_ip(request),
        )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Enregistre les tentatives de connexion échouées dans AuditLog.
    Note: user=None car l'identité n'est pas vérifiée.
    """
    from apps.core.models import AuditLog
    AuditLog.log(
        user=None,
        action_type=AuditLog.ActionType.LOGIN,
        model_name='User',
        object_repr=f"Échec connexion: {credentials.get('username', 'inconnu')}",
        new_value={'username': credentials.get('username', ''), 'success': False},
        ip_address=_get_client_ip(request),
    )
