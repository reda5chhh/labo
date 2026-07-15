import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import BaseModel
from apps.core.mixins import AuditableMixin
from apps.commercial.models import Client, Dossier, generate_reference, generate_date_reference


# ============================================================
# Modèle AOSoumission
# ============================================================

class AOSoumission(AuditableMixin, BaseModel):
    """
    Appel d'Offres (Marché Public) - Phase Soumission et montage du dossier.
    """

    class Statut(models.TextChoices):
        PREPARATION = 'PREPARATION', _('En préparation')
        SOUMIS = 'SOUMIS', _('Soumis / Déposé')
        REJETE = 'REJETE', _('Rejeté / Non retenu')
        ADJUGE = 'ADJUGE', _('Adjugé / Remporté')

    class AOBCType(models.TextChoices):
        AO = 'AO', _('Appel d\'Offres')
        BC = 'BC', _('Bon de Commande')

    class ResultatType(models.TextChoices):
        ADJUGE = 'ADJUGE', _('Adjugé')
        NON_ADJUGE = 'NON_ADJUGE', _('Non adjugé')
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')

    ao_bc = models.CharField(
        _('AO / BC'),
        max_length=2,
        choices=AOBCType.choices,
        default=AOBCType.AO,
    )
    reference_ao = models.CharField(
        _('référence de l\'appel d\'offres'),
        max_length=100,
        unique=True,
        help_text=_('Référence externe officielle de l\'avis d\'AO'),
    )
    client = models.ForeignKey(
        Client,
        verbose_name=_('maître d\'ouvrage (Client)'),
        on_delete=models.PROTECT,
        related_name='appels_offres_soumis',
    )
    objet = models.CharField(
        _('objet du marché'),
        max_length=255,
    )
    lieu_execution = models.CharField(
        _('lieu d\'exécution'),
        max_length=255,
        blank=True,
    )
    date_limite = models.DateField(
        _('date limite de dépôt'),
        help_text=_('Date limite de dépôt des plis'),
    )
    heure_limite = models.TimeField(
        _('heure limite de dépôt'),
        null=True,
        blank=True,
        help_text=_('Heure limite de dépôt des plis'),
    )
    reponse = models.CharField(
        _('réponse'),
        max_length=100,
        blank=True,
    )
    statut_resultat = models.CharField(
        _('résultat'),
        max_length=20,
        choices=ResultatType.choices,
        default=ResultatType.EN_ATTENTE,
    )
    adjudicataire = models.CharField(
        _('adjudicataire'),
        max_length=255,
        blank=True,
    )
    montant = models.DecimalField(
        _('montant'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    estimation_initiale = models.DecimalField(
        _('estimation maître d\'ouvrage'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    montant_soumission = models.DecimalField(
        _('montant de notre soumission'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    statut = models.CharField(
        _('statut de soumission'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.PREPARATION,
    )
    remarques = models.TextField(
        _('remarques / composition du groupement'),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('appel d\'offres soumission')
        verbose_name_plural = _('appels d\'offres soumissions')

    def __str__(self):
        return f"{self.reference_ao} - {self.client.nom} ({self.objet[:30]})"


# ============================================================
# Modèle AOAdjuge
# ============================================================

class AOAdjuge(AuditableMixin, BaseModel):
    """
    Appel d'Offres remporté et notifié. Phase d'exécution du marché.
    """

    class Statut(models.TextChoices):
        EN_COURS = 'EN_COURS', _('En cours d\'exécution')
        TERMINE = 'TERMINE', _('Marché clôturé / Réception définitive')
        RESILIE = 'RESILIE', _('Marché résilié')

    ao_soumission = models.OneToOneField(
        AOSoumission,
        verbose_name=_('appel d\'offres d\'origine'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='adjudication',
    )
    type_marche_bc = models.CharField(
        _('type'),
        max_length=20,
        choices=[('MARCHE', _('Marché')), ('BC', _('Bon de commande'))],
        default='MARCHE',
    )
    num_marche_bc = models.CharField(
        _('N° marché ou BC'),
        max_length=100,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    objet = models.TextField(
        _('objet'),
        blank=True,
    )
    date_adjudication = models.DateField(
        _('date d\'adjudication'),
        default=timezone.now,
    )
    montant_final = models.DecimalField(
        _('montant final adjugé (TTC)'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    caution_definitive_deposee = models.BooleanField(
        _('caution définitive déposée'),
        default=False,
    )
    date_notification = models.DateField(
        _('date de notification de l\'OS'),
        null=True,
        blank=True,
        help_text=_('Ordre de Service de commencement des prestations'),
    )
    delai_realisation = models.CharField(
        _('délai de réalisation'),
        max_length=100,
        blank=True,
    )
    travaux_realises = models.DecimalField(
        _('travaux réalisés'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    reste_a_realiser = models.DecimalField(
        _('reste à réaliser'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    montant_encaisse = models.DecimalField(
        _('montant encaissé'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    acheve = models.BooleanField(
        _('achevé'),
        default=False,
    )
    solde = models.BooleanField(
        _('soldé'),
        default=False,
    )
    statut = models.CharField(
        _('statut d\'exécution'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_COURS,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('appel d\'offres adjugé')
        verbose_name_plural = _('appels d\'offres adjugés')

    def __str__(self):
        ref = self.ao_soumission.reference_ao if self.ao_soumission else self.num_marche_bc
        client_nom = self.ao_soumission.client.nom if (self.ao_soumission and self.ao_soumission.client) else (self.client.nom if self.client else "—")
        return f"Marché {ref} - {client_nom}"

    @property
    def reste_a_encaisser(self):
        return self.montant_final - self.montant_encaisse

    def save(self, *args, **kwargs):
        if self.ao_soumission:
            if not self.client:
                self.client = self.ao_soumission.client
            if not self.objet:
                self.objet = self.ao_soumission.objet
            if not self.montant_final or self.montant_final == 0.00:
                self.montant_final = self.ao_soumission.montant_soumission
        super().save(*args, **kwargs)


# ============================================================
# Modèle Decompte
# ============================================================

class Decompte(AuditableMixin, BaseModel):
    """
    Décompte mensuel ou situation de travaux pour facturer l'avancement.
    """

    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        VALIDE = 'VALIDE', _('Validé par maître d\'œuvre')
        PAYE = 'PAYE', _('Encaissé / Réglé')

    reference = models.CharField(
        _('référence décompte'),
        max_length=50,
        unique=True,
        blank=True,
    )
    ao_adjuge = models.ForeignKey(
        AOAdjuge,
        verbose_name=_('marché lié'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='decomptes',
    )
    dossier = models.ForeignKey(
        Dossier,
        verbose_name=_('dossier de chantier'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='decomptes',
    )
    numero_decompte = models.PositiveIntegerField(
        _('numéro de décompte'),
    )
    date_decompte = models.DateField(
        _('date d\'établissement'),
        default=timezone.now,
    )
    montant_ht = models.DecimalField(
        _('montant H.T.'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    montant_tva = models.DecimalField(
        _('montant TVA'),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    montant_ttc = models.DecimalField(
        _('montant T.T.C.'),
        max_digits=12,
        decimal_places=2,
    )
    chemin_decompte = models.FileField(
        _('chemin décompte'),
        upload_to='decomptes/',
        blank=True,
        null=True,
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('décompte')
        verbose_name_plural = _('décomptes')
        ordering = ['-date_decompte', '-numero_decompte']

    def __str__(self):
        dossier_ref = self.dossier.reference if self.dossier else "—"
        return f"DEC N°{self.numero_decompte} ({self.reference}) - {dossier_ref}"

    def save(self, *args, **kwargs):
        """Génère la référence unique du décompte."""
        if not self.reference:
            self.reference = generate_date_reference('DEC', Decompte, self.date_decompte)
        super().save(*args, **kwargs)


# ============================================================
# Modèle Caution
# ============================================================

class Caution(AuditableMixin, BaseModel):
    """
    Caution bancaire émise par le laboratoire pour un marché public.
    """

    class TypeCaution(models.TextChoices):
        PROVISOIRE = 'PROVISOIRE', _('Caution Provisoire')
        DEFINITIVE = 'DEFINITIVE', _('Caution Définitive')

    class Statut(models.TextChoices):
        DEPOSE = 'DEPOSE', _('Déposée')
        LIBERE = 'LIBERE', _('Libérée / Mainlevée obtenue')
        CONFISQUE = 'CONFISQUE', _('Confisquée par le client')

    ao_soumission = models.ForeignKey(
        AOSoumission,
        verbose_name=_('appel d\'offres soumission'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cautions',
    )
    ao_adjuge = models.ForeignKey(
        AOAdjuge,
        verbose_name=_('marché adjugé'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cautions',
    )
    numero_caution = models.CharField(
        _('numéro de caution'),
        max_length=100,
        blank=True,
    )
    banque = models.CharField(
        _('banque émettrice'),
        max_length=150,
        blank=True,
    )
    type_caution = models.CharField(
        _('type de caution'),
        max_length=30,
        choices=TypeCaution.choices,
    )
    montant = models.DecimalField(
        _('montant caution (MAD)'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    date_depot = models.DateField(
        _('date de dépôt / émission'),
        default=timezone.now,
    )
    date_mainlevee = models.DateField(
        _('date de mainlevée'),
        null=True,
        blank=True,
    )
    renvoyee_banque = models.BooleanField(
        _('renvoyée à la banque'),
        default=False,
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.DEPOSE,
    )

    num_ao = models.CharField(
        _('n° appel d\'offre'),
        max_length=100,
        blank=True,
    )
    num_marche_bc = models.CharField(
        _('n° marché ou BC'),
        max_length=100,
        blank=True,
    )
    client = models.TextField(
        _('client'),
        blank=True,
    )
    objet = models.TextField(
        _('objet'),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('caution')
        verbose_name_plural = _('cautions')

    def __str__(self):
        return f"Caution {self.get_type_caution_display()} - {self.montant} MAD"

    def save(self, *args, **kwargs):
        if self.ao_soumission:
            if not self.num_ao:
                self.num_ao = self.ao_soumission.reference_ao
            if not self.client:
                self.client = self.ao_soumission.client.nom
            if not self.objet:
                self.objet = self.ao_soumission.objet
        if self.ao_adjuge:
            if not self.num_marche_bc:
                self.num_marche_bc = self.ao_adjuge.num_marche_bc
            if not self.num_ao and self.ao_adjuge.ao_soumission:
                self.num_ao = self.ao_adjuge.ao_soumission.reference_ao
            if not self.client:
                self.client = self.ao_adjuge.client.nom if self.ao_adjuge.client else (self.ao_adjuge.ao_soumission.client.nom if self.ao_adjuge.ao_soumission else "")
            if not self.objet:
                self.objet = self.ao_adjuge.objet or (self.ao_adjuge.ao_soumission.objet if self.ao_adjuge.ao_soumission else "")
        super().save(*args, **kwargs)


# ============================================================
# Modèle ResultatBC
# ============================================================

class ResultatBC(AuditableMixin, BaseModel):
    """
    Résultats de l'adjudication des appels d'offres (AO/BC).
    """

    class EtatReponse(models.TextChoices):
        NON_ATTRIBUE = 'NON_ATTRIBUE', _('Non attribué')
        ADJUGE = 'ADJUGE', _('Adjugé')
        REJETE = 'REJETE', _('Rejeté')

    ao_soumission = models.OneToOneField(
        AOSoumission,
        on_delete=models.CASCADE,
        related_name='resultat',
        verbose_name=_("appel d'offres soumission"),
    )
    nombre_participants = models.PositiveIntegerField(
        _('nombre de participants'),
        default=0,
    )
    entreprise_attributaire = models.CharField(
        _('entreprise attributaire'),
        max_length=255,
        blank=True,
    )
    montant = models.DecimalField(
        _('montant'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    etat_reponse = models.CharField(
        _('état de la réponse'),
        max_length=20,
        choices=EtatReponse.choices,
        default=EtatReponse.NON_ATTRIBUE,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('résultat BC')
        verbose_name_plural = _('résultats BC')

    def __str__(self):
        return f"Résultat pour {self.ao_soumission.reference_ao} - {self.get_etat_reponse_display()}"
