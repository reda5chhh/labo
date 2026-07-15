"""Modèles pour le module Finance (Facturation, Encaissements, Caisse, Fournisseurs) de LABO.COS App."""
import datetime
from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.conf import settings

from apps.core.models import BaseModel
from apps.core.mixins import AuditableMixin


def generate_finance_reference(prefix, model_class, field_name='reference'):
    """
    Génère une référence unique séquentielle par année.
    Format : PREFIX-YYYY-XXXX (Ex: FAC-2026-0001)
    """
    year = datetime.date.today().year
    prefix_year = f"{prefix}-{year}-"
    filter_kwargs = {f"{field_name}__startswith": prefix_year}
    
    last_instance = model_class.objects.filter(**filter_kwargs).order_by(field_name).last()
    if last_instance:
        try:
            val = getattr(last_instance, field_name)
            last_seq = int(val.split('-')[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    return f"{prefix_year}{new_seq:04d}"


class Fournisseur(AuditableMixin, BaseModel):
    """
    Représente un prestataire ou fournisseur externe du laboratoire.
    """
    nom = models.CharField(_('Raison sociale'), max_length=255, unique=True)
    ice = models.CharField(_('ICE'), max_length=15, blank=True, null=True)
    rc = models.CharField(_('R.C.'), max_length=50, blank=True, null=True)
    if_fiscal = models.CharField(_('Identifiant Fiscal'), max_length=50, blank=True, null=True)
    patente = models.CharField(_('Patente'), max_length=50, blank=True, null=True)
    adresse = models.TextField(_('Adresse'), blank=True)
    telephone = models.CharField(_('Téléphone'), max_length=30)
    email = models.EmailField(_('Email'), blank=True, null=True)
    active = models.BooleanField(_('Actif'), default=True)

    class Meta:
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Facture(AuditableMixin, BaseModel):
    """
    Représente une facture client émise par le laboratoire.
    """
    class StatutFacture(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        VALIDEE = 'VALIDEE', _('Validée')
        PAYEE_PARTIEL = 'PAYEE_PARTIEL', _('Payée Partiellement')
        PAYEE = 'PAYEE', _('Payée')
        ANNULEE = 'ANNULEE', _('Annulée')

    class DifficulteRecouvrement(models.TextChoices):
        RECOUVRABLE = 'RECOUVRABLE', _('Recouvrable')
        DIFFICILE = 'DIFFICILE', _('Difficile')
        NON_RECOUVRABLE = 'NON_RECOUVRABLE', _('Non Recouvrable')

    reference = models.CharField(_('N° Facture'), max_length=50, unique=True, blank=True)
    client = models.ForeignKey(
        'commercial.Client',
        on_delete=models.PROTECT,
        related_name='factures',
        verbose_name=_('Client'),
    )
    devis = models.ForeignKey(
        'commercial.Devis',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures',
        verbose_name=_('Devis'),
    )
    dossier = models.ForeignKey(
        'commercial.Dossier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures',
        verbose_name=_('Dossier'),
    )
    decompte = models.ForeignKey(
        'marches.Decompte',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures',
        verbose_name=_('Décompte'),
    )
    date_facture = models.DateField(_('Date Facture'), default=datetime.date.today)
    date_echeance = models.DateField(_('Date d\'échéance'), blank=True, null=True)
    
    bc = models.CharField(_('Bon de commande (BC)'), max_length=100, blank=True, null=True)
    type_facture = models.CharField(_('Type facture'), max_length=50, choices=[('SITUATION', 'Situation'), ('DIRECTE', 'Directe'), ('AVOIR', 'Avoir')], default='DIRECTE')
    delai = models.PositiveIntegerField(_('Délai de règlement (jours)'), default=30)
    avec_ras = models.CharField(_('Avec RAS'), max_length=10, choices=[('Non', 'Non'), ('OUI_10', '10%'), ('OUI_15', '15%')], default='Non')
    projet = models.CharField(_('Projet'), max_length=255, blank=True, null=True)
    commentaire = models.TextField(_('Commentaire'), blank=True, null=True)
    synthese_modification = models.TextField(_('Synthèse de modification'), blank=True, null=True)
    
    montant_ht = models.DecimalField(_('Montant HT'), max_digits=12, decimal_places=2, default=0.00, blank=True, validators=[MinValueValidator(0)])
    taux_tva = models.DecimalField(_('Taux TVA (%)'), max_digits=4, decimal_places=2, default=20.00)
    montant_tva = models.DecimalField(_('Montant TVA'), max_digits=12, decimal_places=2, blank=True, null=True)
    montant_ttc = models.DecimalField(_('Montant TTC'), max_digits=12, decimal_places=2, blank=True, null=True)
    
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=StatutFacture.choices,
        default=StatutFacture.BROUILLON,
    )
    notes = models.TextField(_('Notes / Observations'), blank=True)

    # Suivi d'envoi et logistique (Tableau des détails)
    envoye = models.BooleanField(_('Envoyée'), default=False)
    envoye_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='factures_envoyees',
        verbose_name=_('Envoyée par'),
    )
    date_envoi = models.DateField(_('Date d\'envoi'), null=True, blank=True)
    accuse = models.BooleanField(_('Accusée de réception'), default=False)
    date_accuse = models.DateField(_('Date de l\'accusé'), null=True, blank=True)
    
    # Recouvrement
    validee_par_signature = models.BooleanField(_('Validée par signature'), default=False)
    difficulte_recouvrement = models.CharField(
        _('Difficulté de recouvrement'),
        max_length=20,
        choices=DifficulteRecouvrement.choices,
        default=DifficulteRecouvrement.RECOUVRABLE,
    )

    class Meta:
        verbose_name = _('Facture Client')
        verbose_name_plural = _('Factures Clients')
        ordering = ['-date_facture', '-id']

    def __str__(self):
        return f"{self.reference} - {self.client.nom}"

    @property
    def total_encaissements(self):
        """Calcule le total des encaissements encaissés."""
        from decimal import Decimal
        total = self.encaissements.filter(encaisse=True).aggregate(Sum('montant'))['montant__sum']
        return total or Decimal('0.00')
        
    @property
    def solde(self):
        """Calcule le solde restant à payer."""
        from decimal import Decimal
        total_paye = self.encaissements.filter(encaisse=True).aggregate(Sum('montant'))['montant__sum'] or Decimal('0.00')
        return Decimal(str(self.montant_ttc)) - total_paye

    @property
    def nombre_jours_retard(self):
        """Calcule le nombre de jours de retard par rapport à l'échéance."""
        if self.statut == self.StatutFacture.PAYEE:
            return 0
        if datetime.date.today() > self.date_echeance:
            return (datetime.date.today() - self.date_echeance).days
        return 0

    def save(self, *args, **kwargs):
        # Calcul automatique de la date d'échéance basé sur le délai
        if self.date_facture and self.delai:
            self.date_echeance = self.date_facture + datetime.timedelta(days=self.delai)

        # Calcul automatique des montants de TVA et TTC
        from decimal import Decimal
        if self.montant_ht is not None:
            ht = Decimal(str(self.montant_ht))
            tva_rate = Decimal(str(self.taux_tva))
            self.montant_tva = ht * (tva_rate / Decimal('100'))
            self.montant_ttc = ht + self.montant_tva
        
        # Génération automatique de la référence
        if not self.reference:
            self.reference = generate_finance_reference('FAC', Facture)
            
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        """Calcule les totaux HT, TVA et TTC à partir des lignes."""
        from decimal import Decimal
        total_ht = self.lignes.aggregate(
            total=models.Sum(models.F('prix_unitaire') * models.F('quantite'))
        )['total'] or Decimal('0.00')
        self.montant_ht = total_ht
        self.save()


class LigneFacture(AuditableMixin, BaseModel):
    """
    Ligne de détail d'une Facture (Bordereau des prix).
    """
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name=_('Facture'),
    )
    num_prix = models.CharField(
        _('N° prix'),
        max_length=50,
        blank=True,
    )
    designation = models.CharField(
        _('Désignation'),
        max_length=255,
    )
    unite = models.CharField(
        _('Unité'),
        max_length=50,
        blank=True,
    )
    quantite = models.DecimalField(
        _('Quantité'),
        max_digits=12,
        decimal_places=2,
        default=1.00,
    )
    prix_unitaire = models.DecimalField(
        _('Prix unitaire (H.T)'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    class Meta:
        verbose_name = _('Ligne de Facture')
        verbose_name_plural = _('Lignes de Facture')
        ordering = ['id']

    def __str__(self):
        return f"{self.designation} (x{self.quantite})"

    @property
    def prix_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.facture.recalculate_totals()

    def delete(self, *args, **kwargs):
        facture = self.facture
        super().delete(*args, **kwargs)
        facture.recalculate_totals()




class Encaissement(AuditableMixin, BaseModel):
    """
    Représente un règlement reçu d'un client pour une facture donnée.
    """
    class MoyenPaiement(models.TextChoices):
        VIREMENT = 'VIREMENT', _('Virement')
        CHEQUE = 'CHEQUE', _('Chèque')
        EFFET = 'EFFET', _('Effet')
        ESPECES = 'ESPECES', _('Espèces')
        VERSEMENT = 'VERSEMENT', _('Versement Direct')

    reference = models.CharField(_('Réf Encaissement'), max_length=50, unique=True, blank=True)
    facture = models.ForeignKey(
        Facture,
        on_delete=models.CASCADE,
        related_name='encaissements',
        verbose_name=_('Facture'),
    )
    date_encaissement = models.DateField(_('Date d\'encaissement'), default=datetime.date.today)
    montant = models.DecimalField(_('Montant Encaissé'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    moyen_paiement = models.CharField(
        _('Moyen de paiement'),
        max_length=20,
        choices=MoyenPaiement.choices,
    )
    reference_transaction = models.CharField(
        _('Réf Transaction / N° Chèque'),
        max_length=100,
        help_text=_('N° de chèque, référence virement, etc.'),
    )
    banque = models.CharField(_('Banque émettrice'), max_length=150, blank=True)
    compte_depot = models.CharField(_('Compte de dépôt'), max_length=100, blank=True)
    encaisse = models.BooleanField(_('Déposé/Encaissé'), default=True)

    class Meta:
        verbose_name = _('Encaissement')
        verbose_name_plural = _('Encaissements')
        ordering = ['-date_encaissement', '-id']

    def __str__(self):
        return f"{self.reference} - {self.montant} DH"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_finance_reference('ENC', Encaissement)
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut de la facture associée
        facture = self.facture
        solde_restant = facture.solde
        
        if solde_restant <= 0:
            facture.statut = Facture.StatutFacture.PAYEE
        elif solde_restant < facture.montant_ttc:
            facture.statut = Facture.StatutFacture.PAYEE_PARTIEL
        facture.save()

        # Si payé en espèces, enregistrer automatiquement un mouvement de caisse
        if is_new and self.moyen_paiement == self.MoyenPaiement.ESPECES and self.encaisse:
            MouvementCaisse.objects.create(
                date_mouvement=self.date_encaissement,
                type_mouvement=MouvementCaisse.TypeMouvement.ENTREE,
                montant=self.montant,
                motif=f"Encaissement client - Facture {facture.reference}",
                encaissement=self,
            )


class FactureFournisseur(AuditableMixin, BaseModel):
    """
    Représente une facture d'achat reçue d'un fournisseur.
    """
    class StatutFactureFournisseur(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente')
        PAYEE_PARTIEL = 'PAYEE_PARTIEL', _('Payée Partiellement')
        PAYEE = 'PAYEE', _('Payée')
        ANNULEE = 'ANNULEE', _('Annulée')

    reference_interne = models.CharField(_('Réf Interne'), max_length=50, unique=True, blank=True)
    reference_fournisseur = models.CharField(_('N° Facture Fournisseur'), max_length=100)
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.PROTECT,
        related_name='factures',
        verbose_name=_('Fournisseur'),
    )
    date_facture = models.DateField(_('Date Facture'))
    date_echeance = models.DateField(_('Date d\'échéance'))
    
    montant_ht = models.DecimalField(_('Montant HT'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    montant_tva = models.DecimalField(_('Montant TVA'), max_digits=12, decimal_places=2, default=0.00)
    montant_ttc = models.DecimalField(_('Montant TTC'), max_digits=12, decimal_places=2)
    
    statut = models.CharField(
        _('Statut'),
        max_length=20,
        choices=StatutFactureFournisseur.choices,
        default=StatutFactureFournisseur.EN_ATTENTE,
    )

    class Meta:
        verbose_name = _('Facture Fournisseur')
        verbose_name_plural = _('Factures Fournisseurs')
        ordering = ['-date_facture', '-id']

    def __str__(self):
        return f"{self.reference_interne} ({self.reference_fournisseur}) - {self.fournisseur.nom}"

    @property
    def solde(self):
        from decimal import Decimal
        total_paye = self.paiements.aggregate(Sum('montant'))['montant__sum'] or Decimal('0.00')
        return Decimal(str(self.montant_ttc)) - total_paye

    def save(self, *args, **kwargs):
        if not self.reference_interne:
            self.reference_interne = generate_finance_reference('FF', FactureFournisseur, 'reference_interne')
        super().save(*args, **kwargs)


class Paiement(AuditableMixin, BaseModel):
    """
    Représente un règlement émis par le laboratoire pour régler une facture fournisseur.
    """
    class MoyenPaiement(models.TextChoices):
        VIREMENT = 'VIREMENT', _('Virement')
        CHEQUE = 'CHEQUE', _('Chèque')
        EFFET = 'EFFET', _('Effet')
        ESPECES = 'ESPECES', _('Espèces')
        VERSEMENT = 'VERSEMENT', _('Versement Direct')

    reference = models.CharField(_('Réf Paiement'), max_length=50, unique=True, blank=True)
    facture_fournisseur = models.ForeignKey(
        FactureFournisseur,
        on_delete=models.CASCADE,
        related_name='paiements',
        verbose_name=_('Facture Fournisseur'),
    )
    date_paiement = models.DateField(_('Date de paiement'), default=datetime.date.today)
    montant = models.DecimalField(_('Montant Payé'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    moyen_paiement = models.CharField(
        _('Moyen de paiement'),
        max_length=20,
        choices=MoyenPaiement.choices,
    )
    reference_transaction = models.CharField(
        _('Réf Transaction / N° Chèque'),
        max_length=100,
    )

    class Meta:
        verbose_name = _('Paiement Fournisseur')
        verbose_name_plural = _('Paiements Fournisseurs')
        ordering = ['-date_paiement', '-id']

    def __str__(self):
        return f"{self.reference} - {self.montant} DH"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_finance_reference('PAI', Paiement)
            
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut de la facture fournisseur
        ff = self.facture_fournisseur
        solde_restant = ff.solde
        
        if solde_restant <= 0:
            ff.statut = FactureFournisseur.StatutFactureFournisseur.PAYEE
        elif solde_restant < ff.montant_ttc:
            ff.statut = FactureFournisseur.StatutFactureFournisseur.PAYEE_PARTIEL
        ff.save()

        # Si payé en espèces, enregistrer automatiquement un mouvement de caisse (Sortie)
        if is_new and self.moyen_paiement == self.MoyenPaiement.ESPECES:
            MouvementCaisse.objects.create(
                date_mouvement=self.date_paiement,
                type_mouvement=MouvementCaisse.TypeMouvement.SORTIE,
                montant=self.montant,
                motif=f"Règlement fournisseur - Facture {ff.reference_interne}",
                paiement=self,
            )


class MouvementCaisse(AuditableMixin, BaseModel):
    """
    Représente une entrée ou sortie de fonds de la petite caisse.
    """
    class TypeMouvement(models.TextChoices):
        ENTREE = 'ENTREE', _('Entrée de fonds')
        SORTIE = 'SORTIE', _('Sortie de fonds')

    reference = models.CharField(_('Réf Caisse'), max_length=50, unique=True, blank=True)
    date_mouvement = models.DateField(_('Date Mouvement'), default=datetime.date.today)
    type_mouvement = models.CharField(
        _('Type de mouvement'),
        max_length=10,
        choices=TypeMouvement.choices,
    )
    montant = models.DecimalField(_('Montant'), max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    motif = models.CharField(_('Motif / Description'), max_length=255)
    
    encaissement = models.ForeignKey(
        Encaissement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_caisse',
        verbose_name=_('Encaissement Client'),
    )
    paiement = models.ForeignKey(
        Paiement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_caisse',
        verbose_name=_('Paiement Fournisseur'),
    )

    class Meta:
        verbose_name = _('Mouvement de Caisse')
        verbose_name_plural = _('Mouvements de Caisse')
        ordering = ['-date_mouvement', '-id']

    def __str__(self):
        prefix = "+" if self.type_mouvement == self.TypeMouvement.ENTREE else "-"
        return f"{self.reference} ({prefix}{self.montant} DH) - {self.motif}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_finance_reference('CS', MouvementCaisse)
        super().save(*args, **kwargs)


class Recouvrement(AuditableMixin, BaseModel):
    """
    Représente le dossier de recouvrement d'une facture non soldée.
    """
    class StatutRecouvrement(models.TextChoices):
        A_RAPPELER = 'A_RAPPELER', _('À rappeler')
        RELANCE_1 = 'RELANCE_1', _('Relance 1 envoyée')
        RELANCE_2 = 'RELANCE_2', _('Relance 2 envoyée')
        CONTENTIEUX = 'CONTENTIEUX', _('Dossier Contentieux')
        RESOLU = 'RESOLU', _('Résolu')

    facture = models.OneToOneField(
        Facture,
        on_delete=models.CASCADE,
        related_name='recouvrement',
        verbose_name=_('Facture'),
    )
    statut_recouvrement = models.CharField(
        _('Statut Recouvrement'),
        max_length=30,
        choices=StatutRecouvrement.choices,
        default=StatutRecouvrement.A_RAPPELER,
    )
    dernier_rappel = models.DateField(_('Dernier rappel'), null=True, blank=True)
    nombre_rappels = models.PositiveIntegerField(_('Nombre de rappels'), default=0)
    commentaires = models.TextField(_('Commentaires de suivi'), blank=True)

    class Meta:
        verbose_name = _('Dossier de Recouvrement')
        verbose_name_plural = _('Dossiers de Recouvrement')

    def __str__(self):
        return f"Recouvrement Facture {self.facture.reference} - {self.get_statut_recouvrement_display()}"
