"""Modèles pour le service technique de LABO.COS App."""
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.core.mixins import AuditableMixin


class Reception(AuditableMixin, BaseModel):
    """
    Représente une réception de prélèvements/échantillons en laboratoire.
    """

    class EtatEssai(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        EN_COURS = 'EN_COURS', _('En cours')
        TERMINE = 'TERMINE', _('Terminé')

    class EtatRapport(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        VALIDE = 'VALIDE', _('Validé')

    num_reception = models.CharField(
        _('N° réception'),
        max_length=50,
        unique=True,
    )
    client = models.ForeignKey(
        'commercial.Client',
        on_delete=models.CASCADE,
        related_name='receptions',
        verbose_name=_('Client'),
    )
    dossier = models.ForeignKey(
        'commercial.Dossier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receptions',
        verbose_name=_('Dossier'),
    )
    date_reception = models.DateField(
        _('Date de réception'),
        default=datetime.date.today,
    )
    nature_echantillon = models.CharField(
        _('Nature de l\'échantillon'),
        max_length=100,
    )
    etat_essai = models.CharField(
        _('État de l\'essai'),
        max_length=20,
        choices=EtatEssai.choices,
        default=EtatEssai.EN_ATTENTE,
    )
    etat_rapport = models.CharField(
        _('État du rapport'),
        max_length=20,
        choices=EtatRapport.choices,
        default=EtatRapport.BROUILLON,
    )
    charge_prelevement = models.CharField(
        _('Chargé de prélèvement'),
        max_length=150,
        blank=True,
    )
    facture = models.ForeignKey(
        'finance.Facture',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receptions',
        verbose_name=_('Facture'),
    )
    bordereau = models.CharField(
        _('N° Bordereau d\'envoi'),
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = _('Réception')
        verbose_name_plural = _('Réceptions')
        ordering = ['-date_reception', '-id']

    def __str__(self):
        return f"{self.num_reception} - {self.client.nom}"
