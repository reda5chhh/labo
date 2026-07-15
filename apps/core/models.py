"""
LABO.COS App — Modèles de l'application core.

Contient :
- BaseModel : modèle abstrait commun à toutes les applications.
- User : modèle utilisateur personnalisé.
- AuditLog : journal d'audit complet de toutes les actions.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder


# ============================================================
# Managers pour Soft Delete
# ============================================================

class ActiveManager(models.Manager):
    """
    Manager par défaut : exclut les enregistrements annulés.
    Utilisé pour toutes les requêtes normales (listes, FK, etc.).
    """
    def get_queryset(self):
        return super().get_queryset().filter(est_annule=False)


class AllObjectsManager(models.Manager):
    """
    Manager complet : inclut les enregistrements annulés.
    Accessible via Model.objects_all.all()
    """
    def get_queryset(self):
        return super().get_queryset()


# ============================================================
# Modèle Abstrait de Base
# ============================================================

class BaseModel(models.Model):
    """
    Modèle abstrait commun à toutes les entités métier.

    Fournit automatiquement les champs de traçabilité :
    - created_at / updated_at : horodatage automatique
    - created_by / updated_by : utilisateur responsable (ForeignKey lazy)
    """
    created_at = models.DateTimeField(
        _('créé le'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('modifié le'),
        auto_now=True,
    )
    created_by = models.ForeignKey(
        'core.User',
        verbose_name=_('créé par'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+',
    )
    updated_by = models.ForeignKey(
        'core.User',
        verbose_name=_('modifié par'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='+',
    )

    # ── Soft Delete (Annulation) ──
    est_annule = models.BooleanField(
        _('est annulé'),
        default=False,
        db_index=True,
        help_text=_('Si True, cet enregistrement est annulé (non supprimé physiquement).'),
    )
    annule_le = models.DateTimeField(
        _('annulé le'),
        null=True,
        blank=True,
    )
    annule_par = models.ForeignKey(
        'core.User',
        verbose_name=_('annulé par'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    # Manager actif par défaut (cache les annulés)
    objects = ActiveManager()
    # Manager complet (inclut les annulés)
    objects_all = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']


# ============================================================
# Utilisateur Personnalisé
# ============================================================

class User(AbstractUser):
    """
    Utilisateur personnalisé héritant d'AbstractUser Django.

    Ajoute les champs spécifiques au laboratoire :
    - fonction : poste occupé au sein du laboratoire
    - signature_image : image de la signature manuscrite numérisée
    - est_admin : drapeau indiquant si l'utilisateur est administrateur du système
    """
    fonction = models.CharField(
        _('fonction'),
        max_length=150,
        blank=True,
    )
    signature_image = models.ImageField(
        _('image de signature'),
        upload_to='signatures/',
        null=True,
        blank=True,
        help_text=_('Signature manuscrite numérisée (PNG transparent recommandé)'),
    )
    est_admin = models.BooleanField(
        _('est administrateur'),
        default=False,
        help_text=_('Accès au module Paramétrage et aux fonctions d\'administration.'),
    )

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.username

    @property
    def nom_complet(self):
        """Retourne le nom complet (prénom + nom)."""
        return self.get_full_name() or self.username


# ============================================================
# Journal d'Audit
# ============================================================

class AuditLog(models.Model):
    """
    Journal d'audit complet : enregistre toutes les actions critiques
    effectuées par les utilisateurs (création, modification, suppression,
    connexion, validation).

    Ce modèle est peuplé automatiquement par :
    - AuditLogMiddleware : pour les connexions/déconnexions
    - AuditableMixin : pour les opérations CRUD sur les modèles métier
    """

    class ActionType(models.TextChoices):
        CREATE = 'CREATE', _('Création')
        UPDATE = 'UPDATE', _('Modification')
        DELETE = 'DELETE', _('Suppression')
        CANCEL = 'CANCEL', _('Annulation')
        RESTORE = 'RESTORE', _('Restauration')
        LOGIN = 'LOGIN', _('Connexion')
        LOGOUT = 'LOGOUT', _('Déconnexion')
        VALIDATE = 'VALIDATE', _('Validation')
        PRINT = 'PRINT', _('Impression')
        UPLOAD = 'UPLOAD', _('Upload fichier')
        DOWNLOAD = 'DOWNLOAD', _('Téléchargement')

    user = models.ForeignKey(
        User,
        verbose_name=_('utilisateur'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action_type = models.CharField(
        _('type d\'action'),
        max_length=20,
        choices=ActionType.choices,
    )
    model_name = models.CharField(
        _('modèle'),
        max_length=100,
        blank=True,
    )
    object_id = models.PositiveIntegerField(
        _('ID objet'),
        null=True,
        blank=True,
    )
    object_repr = models.CharField(
        _('représentation objet'),
        max_length=255,
        blank=True,
        help_text=_('Représentation textuelle de l\'objet au moment de l\'action'),
    )
    old_value = models.JSONField(
        _('ancienne valeur'),
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder,
    )
    new_value = models.JSONField(
        _('nouvelle valeur'),
        null=True,
        blank=True,
        encoder=DjangoJSONEncoder,
    )
    ip_address = models.GenericIPAddressField(
        _('adresse IP'),
        null=True,
        blank=True,
    )
    user_agent = models.CharField(
        _('agent utilisateur'),
        max_length=255,
        blank=True,
    )
    timestamp = models.DateTimeField(
        _('horodatage'),
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = _('journal d\'audit')
        verbose_name_plural = _('journaux d\'audit')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action_type', '-timestamp']),
        ]

    def __str__(self):
        return (
            f"[{self.get_action_type_display()}] "
            f"{self.user} - {self.model_name} "
            f"#{self.object_id} ({self.timestamp:%d/%m/%Y %H:%M})"
        )

    @classmethod
    def log(
        cls,
        user,
        action_type,
        model_name='',
        object_id=None,
        object_repr='',
        old_value=None,
        new_value=None,
        ip_address=None,
        user_agent='',
    ):
        """
        Méthode utilitaire pour créer un enregistrement d'audit.

        Args:
            user: Instance User ou None.
            action_type: Une valeur de ActionType (ex: 'CREATE').
            model_name: Nom du modèle concerné.
            object_id: Clé primaire de l'objet concerné.
            object_repr: Représentation textuelle de l'objet.
            old_value: Dictionnaire de l'état avant modification.
            new_value: Dictionnaire de l'état après modification.
            ip_address: Adresse IP de la requête.
            user_agent: User-Agent du navigateur.

        Returns:
            Instance AuditLog créée.
        """
        return cls.objects.create(
            user=user,
            action_type=action_type,
            model_name=model_name,
            object_id=object_id,
            object_repr=object_repr,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            user_agent=user_agent,
        )
