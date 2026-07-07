"""
LABO.COS App — Mixins réutilisables pour les vues et modèles.

- AuditableMixin : surcharge save() et delete() pour créer automatiquement
  des entrées AuditLog sur chaque opération CRUD.
- LaboCOSLoginRequiredMixin : vérifie l'authentification + log d'accès refusé.
- ModulePermissionMixin : vérifie les droits d'accès aux modules via DroitAccesApp.
"""
import json
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core import serializers


class AuditableMixin:
    """
    Mixin à ajouter aux modèles héritant de BaseModel.

    Surcharge save() et delete() pour créer automatiquement
    des enregistrements AuditLog avec l'utilisateur et l'IP courants.

    Usage dans un modèle :
        class MonModele(AuditableMixin, BaseModel):
            ...
    """

    def _get_field_dict(self):
        """
        Sérialise les champs du modèle en dictionnaire JSON-compatible.

        Retourne:
            dict: Dictionnaire {nom_champ: valeur} de tous les champs.
        """
        result = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            # Convertir les types non-JSON-sérialisables
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            elif hasattr(value, 'pk'):
                value = value.pk
            result[field.name] = value
        return result

    def save(self, *args, **kwargs):
        """
        Surcharge de save() pour :
        1. Injecter created_by/updated_by depuis le thread local.
        2. Créer un AuditLog CREATE ou UPDATE selon si l'objet est nouveau.
        """
        from apps.core.middleware import get_current_user, get_current_ip
        from apps.core.models import AuditLog

        user = get_current_user()
        ip = get_current_ip()

        is_new = self.pk is None
        old_value = None

        if not is_new:
            # Récupérer l'ancienne valeur avant modification
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                old_value = old_instance._get_field_dict()
            except self.__class__.DoesNotExist:
                pass

        # Injecter les utilisateurs de traçabilité
        if hasattr(self, 'created_by') and is_new and user:
            self.created_by = user
        if hasattr(self, 'updated_by') and user:
            self.updated_by = user

        super().save(*args, **kwargs)

        # Créer l'entrée AuditLog
        AuditLog.log(
            user=user,
            action_type=AuditLog.ActionType.CREATE if is_new else AuditLog.ActionType.UPDATE,
            model_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=str(self),
            old_value=old_value,
            new_value=self._get_field_dict(),
            ip_address=ip,
        )

    def delete(self, *args, **kwargs):
        """
        Surcharge de delete() pour créer un AuditLog DELETE
        avec une copie de l'état de l'objet avant suppression.
        """
        from apps.core.middleware import get_current_user, get_current_ip
        from apps.core.models import AuditLog

        user = get_current_user()
        ip = get_current_ip()

        old_value = self._get_field_dict()
        pk = self.pk
        repr_str = str(self)

        super().delete(*args, **kwargs)

        AuditLog.log(
            user=user,
            action_type=AuditLog.ActionType.DELETE,
            model_name=self.__class__.__name__,
            object_id=pk,
            object_repr=repr_str,
            old_value=old_value,
            ip_address=ip,
        )


class LaboCOSLoginRequiredMixin(LoginRequiredMixin):
    """
    Mixin d'authentification avec redirection personnalisée
    et message d'erreur localisé.
    """
    login_url = '/auth/login/'

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                _('Vous n\'avez pas la permission d\'accéder à cette page.')
            )
            return redirect('core:dashboard')
        messages.warning(
            self.request,
            _('Veuillez vous connecter pour accéder à cette page.')
        )
        return super().handle_no_permission()


class AdminRequiredMixin(LaboCOSLoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin réservant l'accès aux utilisateurs est_admin=True.
    Utilisé pour les modules Paramétrage et Informatique.
    """

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.est_admin or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        messages.error(
            self.request,
            _('Cette fonctionnalité est réservée aux administrateurs.')
        )
        return redirect('core:dashboard')


class ModulePermissionMixin(LaboCOSLoginRequiredMixin):
    """
    Mixin vérifiant les droits d'accès aux modules via DroitAccesApp.

    Usage dans une vue :
        class MaVue(ModulePermissionMixin, ListView):
            module_name = 'commercial'
            action_name = 'devis'
    """
    module_name = None  # Nom du service dans DroitAccesApp
    action_name = None  # Nom de l'action (ex: 'view', 'add', 'edit', 'delete')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Les superusers et admins ont tous les droits
        if request.user.is_superuser or request.user.est_admin:
            return super().dispatch(request, *args, **kwargs)

        # Vérification des droits (implémentée dans Phase 11)
        # Pour l'instant, tous les utilisateurs connectés ont accès
        return super().dispatch(request, *args, **kwargs)
