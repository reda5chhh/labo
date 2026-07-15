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
        from django.db.models.fields.files import FieldFile
        result = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            # Convertir les types non-JSON-sérialisables
            if isinstance(value, FieldFile):
                value = value.name if value else None
            elif hasattr(value, 'isoformat'):
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
        Annulation logique (Soft Delete) : marque l'objet comme annulé
        sans le supprimer physiquement de la base de données.
        Enregistre un AuditLog CANCEL.
        """
        from django.utils import timezone
        from apps.core.middleware import get_current_user, get_current_ip
        from apps.core.models import AuditLog

        user = get_current_user()
        ip = get_current_ip()
        old_value = self._get_field_dict()

        # Soft delete : on marque l'objet comme annulé
        self.est_annule = True
        self.annule_le = timezone.now()
        self.annule_par = user
        # Appel de save() directement sur la base (bypass AuditableMixin.save)
        super(type(self), self).save(update_fields=['est_annule', 'annule_le', 'annule_par'])

        AuditLog.log(
            user=user,
            action_type=AuditLog.ActionType.CANCEL,
            model_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=str(self),
            old_value=old_value,
            new_value=self._get_field_dict(),
            ip_address=ip,
        )

    def restore(self):
        """
        Restauration : réactive un enregistrement annulé.
        Enregistre un AuditLog RESTORE.
        """
        from apps.core.middleware import get_current_user, get_current_ip
        from apps.core.models import AuditLog

        user = get_current_user()
        ip = get_current_ip()
        old_value = self._get_field_dict()

        self.est_annule = False
        self.annule_le = None
        self.annule_par = None
        super(type(self), self).save(update_fields=['est_annule', 'annule_le', 'annule_par'])

        AuditLog.log(
            user=user,
            action_type=AuditLog.ActionType.RESTORE,
            model_name=self.__class__.__name__,
            object_id=self.pk,
            object_repr=str(self),
            old_value=old_value,
            new_value=self._get_field_dict(),
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
    Mixin vérifiant les droits d'accès aux modules via DroitAcces.

    Usage dans une vue :
        class MaVue(ModulePermissionMixin, ListView):
            module_name = 'commercial'
            action_name = 'view'
    """
    module_name = None  # Nom du service/module dans DroitAcces
    action_name = None  # Nom de l'action (ex: 'view', 'add', 'edit', 'delete')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Les superusers et admins ont tous les droits
        if request.user.is_superuser or request.user.est_admin:
            return super().dispatch(request, *args, **kwargs)

        if not self.module_name:
            return super().dispatch(request, *args, **kwargs)

        # Vérification des droits d'accès
        from django.db.models import Q
        from apps.gestion_droits_acces.models import DroitAcces

        action = self.action_name
        is_list_or_dashboard = (
            hasattr(self, 'object_list') or 
            self.__class__.__name__.endswith('ListView') or 
            self.__class__.__name__.endswith('TemplateView')
        )

        if action == 'view':
            if is_list_or_dashboard:
                # L'utilisateur doit avoir au moins une permission pour voir la page/tableau de bord
                has_perm = DroitAcces.objects.filter(
                    Q(peut_voir=True) | Q(peut_ajouter=True) | Q(peut_modifier=True) | Q(peut_annuler=True),
                    user=request.user,
                    module=self.module_name
                ).exists()
            else:
                # Les vues de détails nécessitent le droit 'voir'
                has_perm = DroitAcces.objects.filter(
                    user=request.user,
                    module=self.module_name,
                    peut_voir=True
                ).exists()
        else:
            perm_field = 'peut_voir'
            if action == 'add':
                perm_field = 'peut_ajouter'
            elif action == 'edit':
                perm_field = 'peut_modifier'
            elif action in ('delete', 'cancel'):
                perm_field = 'peut_annuler'

            has_perm = DroitAcces.objects.filter(
                user=request.user,
                module=self.module_name,
                **{perm_field: True}
            ).exists()

        if not has_perm:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Sécurité supplémentaire au niveau de la base de données
        qs = super().get_queryset()
        if self.module_name:
            if not (self.request.user.is_superuser or self.request.user.est_admin):
                from apps.gestion_droits_acces.models import DroitAcces
                has_view = DroitAcces.objects.filter(
                    user=self.request.user,
                    module=self.module_name,
                    peut_voir=True
                ).exists()
                if not has_view:
                    return qs.none()
        return qs


    def get_context_data(self, **kwargs):
        context = {}
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(**kwargs)
        
        if self.module_name:
            if self.request.user.is_superuser or self.request.user.est_admin:
                class AdminDroit:
                    peut_voir = True
                    peut_ajouter = True
                    peut_modifier = True
                    peut_annuler = True
                context['perms_module'] = AdminDroit()
            else:
                from apps.gestion_droits_acces.models import DroitAcces
                try:
                    droit = DroitAcces.objects.get(user=self.request.user, module=self.module_name)
                    context['perms_module'] = droit
                except DroitAcces.DoesNotExist:
                    class DummyDroit:
                        peut_voir = False
                        peut_ajouter = False
                        peut_modifier = False
                        peut_annuler = False
                    context['perms_module'] = DummyDroit()
        return context

