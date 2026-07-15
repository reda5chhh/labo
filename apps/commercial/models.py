"""
LABO.COS App — Modèles de l'application commercial.

Gère tout le cycle de vie de la relation client et des contrats :
- Client : base des tiers
- RevueDemande : étude de faisabilité technique
- Devis : offres de prix
- Dossier : exécution des affaires
- Convention : marchés cadres
- AOSoumission / AOAdjuge : marchés publics / appels d'offres
- Caution : garanties bancaires
- Decompte : avancement des travaux
- BonLivraison / DetailBonLivraison : livraison des rapports/PV
- ResultatBC : évaluation satisfaction et clôture
"""
import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import BaseModel
from apps.core.mixins import AuditableMixin


# ============================================================
# Utilitaires de génération de références uniques
# ============================================================

def generate_reference(prefix, model_class):
    """
    Génère une référence unique séquentielle par année.
    Format : PREFIX-YYYY-XXXX (Ex: DEV-2026-0001)

    Args:
        prefix (str): Le préfixe du modèle (ex: 'DEV', 'DOS')
        model_class (models.Model): La classe du modèle cible

    Returns:
        str: La référence unique générée.
    """
    year = datetime.date.today().year
    prefix_year = f"{prefix}-{year}-"
    # Recherche du dernier enregistrement de la même année
    last_instance = model_class.objects.filter(reference__startswith=prefix_year).order_by('reference').last()
    if last_instance:
        try:
            # Récupère les 4 derniers chiffres
            last_seq = int(last_instance.reference.split('-')[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    return f"{prefix_year}{new_seq:04d}"


def generate_date_reference(prefix, model_class, date_value):
    """
    Génère une référence unique basée sur la date choisie.
    Format : PREFIX YYMMDD-XXX (Ex: DEV 260711-001)
    """
    if not date_value:
        date_value = datetime.date.today()
    elif isinstance(date_value, datetime.datetime):
        date_value = date_value.date()
        
    yymmdd = date_value.strftime('%y%m%d')
    prefix_day = f"{prefix} {yymmdd}-"
    
    # On récupère le dernier enregistrement du même jour en incluant les objets annulés
    last_instance = None
    if hasattr(model_class, 'objects_all'):
        last_instance = model_class.objects_all.filter(reference__startswith=prefix_day).order_by('reference').last()
    else:
        last_instance = model_class.objects.filter(reference__startswith=prefix_day).order_by('reference').last()
        
    if last_instance:
        try:
            # Récupère le dernier compteur après le tiret
            last_seq = int(last_instance.reference.split('-')[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
    return f"{prefix_day}{new_seq:03d}"


# ============================================================
# 1. Modèle Client
# ============================================================

class Client(AuditableMixin, BaseModel):
    """
    Représente un client (compte tiers) du laboratoire.
    """

    class ClientType(models.TextChoices):
        ENTREPRISE = 'ENTREPRISE', _('Entreprise Privée')
        PARTICULIER = 'PARTICULIER', _('Particulier')
        ETAT = 'ETAT', _('Organisme Public / État')

    nom = models.CharField(
        _('nom / raison sociale'),
        max_length=255,
        unique=True,
    )
    type_client = models.CharField(
        _('type de client'),
        max_length=20,
        choices=ClientType.choices,
        default=ClientType.ENTREPRISE,
    )
    ice = models.CharField(
        _('ICE'),
        max_length=15,
        blank=True,
        null=True,
        help_text=_('Identifiant Commun de l\'Entreprise (15 chiffres)'),
    )
    rc = models.CharField(
        _('R.C.'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Registre du Commerce'),
    )
    patente = models.CharField(
        _('patente'),
        max_length=50,
        blank=True,
        null=True,
    )
    if_fiscal = models.CharField(
        _('identifiant fiscal'),
        max_length=50,
        blank=True,
        null=True,
    )
    adresse = models.TextField(
        _('adresse'),
    )
    telephone = models.CharField(
        _('téléphone principal'),
        max_length=30,
    )
    email = models.EmailField(
        _('email général'),
        blank=True,
        null=True,
    )
    # Contacts de facturation/suivi
    contact_nom = models.CharField(
        _('nom de l\'interlocuteur'),
        max_length=100,
        blank=True,
    )
    contact_telephone = models.CharField(
        _('téléphone de l\'interlocuteur'),
        max_length=30,
        blank=True,
    )
    contact_email = models.EmailField(
        _('email de l\'interlocuteur'),
        blank=True,
    )
    solde_initial = models.DecimalField(
        _('solde initial'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_('Solde de départ lors de la mise en service du système'),
    )
    active = models.BooleanField(
        _('actif'),
        default=True,
    )
    ville = models.CharField(
        _('ville'),
        max_length=100,
        blank=True,
    )
    telephone_2 = models.CharField(
        _('téléphone 2'),
        max_length=30,
        blank=True,
    )
    mle = models.CharField(
        _('mle'),
        max_length=50,
        blank=True,
    )
    representant = models.CharField(
        _('représentant'),
        max_length=150,
        blank=True,
    )
    cin = models.CharField(
        _('CIN'),
        max_length=50,
        blank=True,
    )
    gsm = models.CharField(
        _('GSM'),
        max_length=30,
        blank=True,
    )
    fax = models.CharField(
        _('Fax'),
        max_length=30,
        blank=True,
    )
    synthese_modification = models.TextField(
        _('synthèse de modification'),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        ordering = ['nom']

    def __str__(self):
        return self.nom


# ============================================================
# 2. Modèle RevueDemande
# ============================================================

class RevueDemande(AuditableMixin, BaseModel):
    """
    Étude de faisabilité et revue de contrat (Norme ISO 17025).
    S'assure que le labo a les moyens techniques de réaliser la prestation.
    """

    class Statut(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', _('En attente de revue')
        ACCEPTE = 'ACCEPTE', _('Demande acceptée')
        REFUSE = 'REFUSE', _('Demande refusée')

    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.PROTECT,
        related_name='revues_demandes',
    )
    date_demande = models.DateField(
        _('date de la demande'),
        default=timezone.now,
    )
    objet = models.CharField(
        _('objet du projet'),
        max_length=255,
    )
    description = models.TextField(
        _('description des prestations'),
        blank=True,
    )
    exigences_techniques = models.BooleanField(
        _('exigences techniques définies'),
        default=True,
        help_text=_('Les exigences techniques sont-elles définies, documentées et comprises ?'),
    )
    capacite_equipement = models.BooleanField(
        _('équipements disponibles'),
        default=True,
        help_text=_('Le laboratoire dispose-t-il des équipements et matériels requis ?'),
    )
    competence_personnel = models.BooleanField(
        _('personnel qualifié disponible'),
        default=True,
        help_text=_('Le personnel a-t-il les compétences nécessaires pour ces essais ?'),
    )
    delais_respectes = models.BooleanField(
        _('délais réalisables'),
        default=True,
        help_text=_('Les délais demandés par le client peuvent-ils être respectés ?'),
    )
    statut = models.CharField(
        _('statut de faisabilité'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
    )
    remarques = models.TextField(
        _('remarques / actions correctives'),
        blank=True,
    )
    reference = models.CharField(
        _('référence revue'),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    TYPE_REVUE_CHOICES = [
        ('DEMANDE', _('Demande')),
        ('CONTRAT', _('Contrat')),
        ('AVENANT', _('Avenant')),
    ]
    type_revue = models.CharField(
        _('type de revue'),
        max_length=100,
        choices=TYPE_REVUE_CHOICES,
        default='DEMANDE',
        blank=True,
    )
    decision_labo = models.CharField(
        _('décision labo'),
        max_length=20,
        choices=[('ACCORD', 'Accordé'), ('REFUS', 'Refusé'), ('ATTENTE', 'En attente')],
        default='ATTENTE',
    )
    accord_client = models.CharField(
        _('accord client'),
        max_length=20,
        choices=[('ACCORD', 'Accordé'), ('REFUS', 'Refusé'), ('ATTENTE', 'En attente')],
        default='ATTENTE',
    )
    dossier = models.ForeignKey(
        'Dossier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revues',
        verbose_name=_('Dossier'),
    )
    ref_piece_jointe = models.CharField(
        _('référence pièce jointe'),
        max_length=100,
        blank=True,
    )
    ref_ao_bc = models.CharField(
        _('référence AO/BC'),
        max_length=100,
        blank=True,
    )
    lieu_execution = models.CharField(
        _("lieu d'exécution"),
        max_length=255,
        blank=True,
    )
    TYPE_RECEPTION_CHOICES = [
        ('Au laboratoire', _('Au laboratoire')),
        ('Sur chantier', _('Sur chantier')),
        ('Par courrier', _('Par courrier / transporteur')),
    ]
    type_reception_demande = models.CharField(
        _('type réception de la demande'),
        max_length=100,
        choices=TYPE_RECEPTION_CHOICES,
        default='Au laboratoire',
        blank=True,
    )
    NATURE_PRESTATION_CHOICES = [
        ('Essais', _('Essais')),
        ('Etudes', _('Études')),
        ('Controle', _('Contrôle')),
        ('Assistance', _('Assistance technique')),
    ]
    nature_prestation = models.CharField(
        _('nature de la prestation'),
        max_length=100,
        choices=NATURE_PRESTATION_CHOICES,
        default='Essais',
        blank=True,
    )
    ETAT_REVUE_CHOICES = [
        ('Initiale', _('Initiale')),
        ('Modifiee', _('Modifiée')),
        ('Validee', _('Validée')),
    ]
    etat_revue = models.CharField(
        _('état de revue'),
        max_length=100,
        choices=ETAT_REVUE_CHOICES,
        default='Initiale',
        blank=True,
    )
    objet_modification = models.TextField(
        _('objet de modification'),
        blank=True,
    )
    discussion_client = models.TextField(
        _('discussion pertinente avec client'),
        blank=True,
    )
    RESULTAT_CHOICES = [
        ('Proposition transmise au client', _('Proposition transmise au client')),
        ('Faisabilite confirmee', _('Faisabilité confirmée')),
        ('Demande rejetee', _('Demande rejetée')),
    ]
    sortie_resultat = models.CharField(
        _('résultat'),
        max_length=255,
        choices=RESULTAT_CHOICES,
        default='Proposition transmise au client',
        blank=True,
    )
    DECISION_CHOICES = [
        ('OUI', _('Oui')),
        ('NON', _('Non')),
    ]
    sortie_decision = models.CharField(
        _('décision'),
        max_length=50,
        choices=DECISION_CHOICES,
        default='OUI',
        blank=True,
    )
    sortie_pieces_ref = models.CharField(
        _('pièces de référence'),
        max_length=255,
        blank=True,
    )
    validation_date = models.DateField(
        _('réalisée le'),
        null=True,
        blank=True,
    )
    validation_technique = models.CharField(
        _('pour le service technique'),
        max_length=150,
        blank=True,
    )
    
    # Checklist technique
    CHECKLIST_CHOICES = [
        ('OUI', 'Oui'),
        ('NON', 'Non'),
        ('NA', 'N/A'),
    ]
    q1_exigences = models.CharField(_("1. Les exigences du client (données du marché) sont : Définies, Documentées et Comprises"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q1_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q2_methode = models.CharField(_("2. La méthode demandée par le client est appropriée et/ou non périmée"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q2_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q3_incertitudes = models.CharField(_("3. Demande des incertitudes sur les résultats"), max_length=5, choices=CHECKLIST_CHOICES, default='NON')
    q3_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q4_echantillonnage = models.CharField(_("4. Prestation échantillonnage"), max_length=5, choices=CHECKLIST_CHOICES, default='NA')
    q4_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q5_acheminement = models.CharField(_("5. Acheminement des échantillons au laboratoire sous la responsabilité du client"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q5_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q6_conservation = models.CharField(_("6. Période de conservation des échantillons au laboratoire après émission des rapports d'essais"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q6_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q7_soustraitance = models.CharField(_("7. Possibilité de sous-traitance de la prestation"), max_length=5, choices=CHECKLIST_CHOICES, default='NON')
    q7_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q8_transmission = models.CharField(_("8. Les modalités de transmission du rapport"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q8_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q9_cooperation = models.CharField(_("9. Coopération, conseil et informations demandés"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q9_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q10_avis = models.CharField(_("10. Le client demande avis et interprétation"), max_length=5, choices=CHECKLIST_CHOICES, default='NA')
    q10_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q11_declaration = models.CharField(_("11. Le client demande une déclaration de conformité"), max_length=5, choices=CHECKLIST_CHOICES, default='NA')
    q11_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q12_equipements = models.CharField(_("12. Disponibilité et conformité des équipements"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q12_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q13_ressources = models.CharField(_("13. Disponibilité des ressources humaines compétentes"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q13_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)
    
    q14_methodes_choisies = models.CharField(_("14. Les méthodes choisies (norme, etc.) sont appropriées et capables de répondre aux exigences du client"), max_length=5, choices=CHECKLIST_CHOICES, default='OUI')
    q14_note = models.CharField(_("Note / Constat"), max_length=255, blank=True)

    class Meta(BaseModel.Meta):
        verbose_name = _('revue de demande')
        verbose_name_plural = _('revues de demandes')

    def __str__(self):
        return f"{self.reference or self.pk} - {self.client.nom} - {self.objet[:30]}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_date_reference('REV', RevueDemande, self.date_demande)
        super().save(*args, **kwargs)


# ============================================================
# 3. Modèle Devis
# ============================================================

class Devis(AuditableMixin, BaseModel):
    """
    Devis commercial / Offre de prix.
    """

    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        ENVOYE = 'ENVOYE', _('Envoyé au client')
        ACCEPTE = 'ACCEPTE', _('Accepté / Signé')
        REFUSE = 'REFUSE', _('Refusé')
        ANNULE = 'ANNULE', _('Annulé')

    reference = models.CharField(
        _('référence'),
        max_length=50,
        unique=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.PROTECT,
        related_name='devis',
    )
    revue_demande = models.OneToOneField(
        RevueDemande,
        verbose_name=_('revue de demande'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='devis',
    )
    date_devis = models.DateField(
        _('date du devis'),
        default=timezone.now,
    )
    objet = models.CharField(
        _('objet'),
        max_length=255,
    )
    montant_ht = models.DecimalField(
        _('montant H.T.'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )
    taux_tva = models.DecimalField(
        _('taux TVA (%)'),
        max_digits=4,
        decimal_places=2,
        default=20.00,
    )
    montant_tva = models.DecimalField(
        _('montant TVA'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        editable=False,
    )
    montant_ttc = models.DecimalField(
        _('montant T.T.C.'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        editable=False,
    )
    class TypeDevis(models.TextChoices):
        BATIMENT = 'BATIMENT', _('Bâtiment')
        GENIE_CIVIL = 'GENIE_CIVIL', _('Génie Civil')
        ROUTE = 'ROUTE', _('Route / Infrastructure')
        HYDRAULIQUE = 'HYDRAULIQUE', _('Hydraulique')
        GEOTECHNIQUE = 'GEOTECHNIQUE', _('Géotechnique')
        AUTRE = 'AUTRE', _('Autre')

    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
    )
    conditions_reglement = models.TextField(
        _('conditions de règlement'),
        blank=True,
    )
    validite_jours = models.PositiveIntegerField(
        _('durée de validité (jours)'),
        default=90,
    )
    reception_bc = models.BooleanField(
        _('réception BC'),
        default=False,
    )
    ref_bc = models.CharField(
        _('référence BC'),
        max_length=100,
        blank=True,
    )
    type_devis = models.CharField(
        _('type devis'),
        max_length=100,
        choices=TypeDevis.choices,
        blank=True,
    )
    synthese_modification = models.TextField(
        _('synthèse de modification'),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('devis')
        verbose_name_plural = _('devis')

    def __str__(self):
        return f"{self.reference} - {self.client.nom} ({self.montant_ttc} MAD)"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_date_reference('DEV', Devis, self.date_devis)
        if self.montant_ht:
            from decimal import Decimal
            self.montant_tva = Decimal(str(self.montant_ht)) * (Decimal(str(self.taux_tva)) / Decimal('100.00'))
            self.montant_ttc = Decimal(str(self.montant_ht)) + self.montant_tva
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        from decimal import Decimal
        # Sum of all details
        totals = self.details.aggregate(
            total_ht=models.Sum(models.F('quantite') * models.F('prix_unitaire'))
        )
        self.montant_ht = totals['total_ht'] or Decimal('0.00')
        self.montant_tva = Decimal(str(self.montant_ht)) * (Decimal(str(self.taux_tva)) / Decimal('100.00'))
        self.montant_ttc = Decimal(str(self.montant_ht)) + self.montant_tva
        Devis.objects.filter(pk=self.pk).update(
            montant_ht=self.montant_ht,
            montant_tva=self.montant_tva,
            montant_ttc=self.montant_ttc
        )


# ============================================================
# 4. Modèle Dossier
# ============================================================

class Dossier(AuditableMixin, BaseModel):
    """
    Dossier d'affaire / Chantier en cours d'exécution.
    """

    class Statut(models.TextChoices):
        EN_COURS = 'EN_COURS', _('En cours')
        CLOTURE = 'CLOTURE', _('Clôturé')
        ANNULE = 'ANNULE', _('Annulé')

    class TypeAffaire(models.TextChoices):
        BATIMENT = 'BATIMENT', _('Bâtiment')
        GENIE_CIVIL = 'GENIE_CIVIL', _('Génie Civil')
        ROUTE = 'ROUTE', _('Route / Infrastructure')
        HYDRAULIQUE = 'HYDRAULIQUE', _('Hydraulique')
        GEOTECHNIQUE = 'GEOTECHNIQUE', _('Géotechnique')
        AUTRE = 'AUTRE', _('Autre')

    class ModeReglement(models.TextChoices):
        ESPECES = 'ESPECES', _('Espèces')
        CHEQUE = 'CHEQUE', _('Chèque')
        VIREMENT = 'VIREMENT', _('Virement Bancaire')
        TRAITE = 'TRAITE', _('Traite (LCN)')

    class EcheanceFacturation(models.TextChoices):
        RECEPTION = 'RECEPTION', _('A la réception')
        FIN_MOIS = 'FIN_MOIS', _('Fin de mois')
        TRENTE_JOURS = '30_JOURS', _('A 30 jours')
        SOIXANTE_JOURS = '60_JOURS', _('A 60 jours')

    reference = models.CharField(
        _('référence dossier'),
        max_length=50,
        unique=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.PROTECT,
        related_name='dossiers',
    )
    devis = models.ForeignKey(
        Devis,
        verbose_name=_('devis d\'origine'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='dossiers',
    )
    nom_projet = models.CharField(
        _('nom du projet / affaire'),
        max_length=255,
    )
    emplacement = models.CharField(
        _('lieu des travaux'),
        max_length=255,
        blank=True,
    )
    date_ouverture = models.DateField(
        _('date d\'ouverture'),
        default=timezone.now,
    )
    date_cloture = models.DateField(
        _('date de clôture'),
        null=True,
        blank=True,
    )
    chef_projet = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('responsable / chef de projet'),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='dossiers_diriges',
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.EN_COURS,
    )
    prestation = models.CharField(
        _('prestation'),
        max_length=100,
        blank=True,
    )
    commande = models.CharField(
        _('commande'),
        max_length=100,
        blank=True,
    )
    etat_accreditation = models.CharField(
        _("état d'accréditation"),
        max_length=20,
        choices=[('ACCREDITE', 'Accrédité'), ('NON_ACCREDITE', 'Non accrédité')],
        default='NON_ACCREDITE',
    )
    type_affaire = models.CharField(
        _('type affaire'),
        max_length=100,
        choices=TypeAffaire.choices,
        default=TypeAffaire.BATIMENT,
    )
    date_os = models.DateField(
        _("date de l'ordre de service"),
        null=True,
        blank=True,
    )
    entreprise = models.CharField(
        _('entreprise'),
        max_length=255,
        blank=True,
    )
    commentaire = models.TextField(
        _('commentaire'),
        blank=True,
    )
    mode_reglement = models.CharField(
        _('mode de règlement'),
        max_length=50,
        choices=ModeReglement.choices,
        default=ModeReglement.VIREMENT,
    )
    delai_paiement = models.IntegerField(
        _('délai de paiement (jours)'),
        default=0,
    )
    echeance_facturation = models.CharField(
        _('échéance de facturation'),
        max_length=100,
        choices=EcheanceFacturation.choices,
        default=EcheanceFacturation.RECEPTION,
    )
    synthese_modification = models.TextField(
        _('synthèse de modification'),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('dossier')
        verbose_name_plural = _('dossiers')

    def __str__(self):
        return f"{self.reference} - {self.nom_projet[:40]} ({self.client.nom})"

    def save(self, *args, **kwargs):
        """Génère la référence unique du dossier."""
        if not self.reference:
            self.reference = generate_date_reference('DOS', Dossier, self.date_ouverture)
        super().save(*args, **kwargs)


# ============================================================
# 5. Modèle Convention
# ============================================================

class Convention(AuditableMixin, BaseModel):
    """
    Convention de partenariat / Accord-cadre à long terme avec tarifs négociés.
    """

    class Statut(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        SUSPENDUE = 'SUSPENDUE', _('Suspendue')
        TERMINEE = 'TERMINEE', _('Terminée')

    reference = models.CharField(
        _('numéro de convention'),
        max_length=50,
        unique=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        verbose_name=_('client'),
        on_delete=models.PROTECT,
        related_name='conventions',
    )
    objet = models.CharField(
        _('objet'),
        max_length=255,
    )
    date_debut = models.DateField(
        _('date de début'),
        default=timezone.now,
    )
    date_fin = models.DateField(
        _('date de fin'),
        null=True,
        blank=True,
    )
    tarif_specifique = models.TextField(
        _('conditions tarifaires spécifiques'),
        blank=True,
        help_text=_('Décrire les remises, bordereaux de prix négociés ou conditions spéciales'),
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.ACTIVE,
    )
    validee_par_client = models.BooleanField(
        _('validée par client'),
        default=False,
    )



    class Meta(BaseModel.Meta):
        verbose_name = _('convention')
        verbose_name_plural = _('conventions')

    def __str__(self):
        return f"{self.reference} - {self.client.nom} ({self.get_statut_display()})"

    def save(self, *args, **kwargs):
        """Génère la référence unique de la convention."""
        if not self.reference:
            self.reference = generate_date_reference('CONV', Convention, self.date_debut)
        super().save(*args, **kwargs)


# Modèles de Marchés déplacés vers l'application marches


# ============================================================
# 10. Modèle BonLivraison
# ============================================================

class BonLivraison(AuditableMixin, BaseModel):
    """
    Bon de Livraison (BL) confirmant la remise physique des rapports,
    PV ou procès-verbaux de contrôle.
    """

    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', _('Brouillon')
        VALIDE = 'VALIDE', _('Validé')
        ENVOYE = 'ENVOYE', _('Envoyé / Remis au client')

    reference = models.CharField(
        _('référence BL'),
        max_length=50,
        unique=True,
        blank=True,
    )
    dossier = models.ForeignKey(
        Dossier,
        verbose_name=_('dossier lié'),
        on_delete=models.PROTECT,
        related_name='bons_livraison',
    )
    date_bl = models.DateField(
        _('date de livraison'),
        default=timezone.now,
    )
    destinataire = models.CharField(
        _('réceptionné par (destinataire)'),
        max_length=255,
        blank=True,
        help_text=_('Nom de la personne physique qui reçoit les PV'),
    )
    statut = models.CharField(
        _('statut'),
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
    )
    saisie_le = models.DateTimeField(
        _('saisie le'),
        default=timezone.now,
    )
    date_envoi = models.DateField(
        _("date d'envoi"),
        null=True,
        blank=True,
    )
    envoi_par = models.CharField(
        _("envoi par"),
        max_length=150,
        blank=True,
    )
    envoye = models.BooleanField(
        _("envoyé"),
        default=False,
    )
    accuse = models.BooleanField(
        _("accusé de réception"),
        default=False,
    )
    date_accuse = models.DateField(
        _("date d'accusé"),
        null=True,
        blank=True,
    )
    objet = models.TextField(
        _("objet de la livraison"),
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('bon de livraison')
        verbose_name_plural = _('bons de livraison')

    def __str__(self):
        return f"{self.reference} - {self.dossier.reference} ({self.date_bl})"

    def save(self, *args, **kwargs):
        """Génère la référence unique du bon de livraison et remplit l'objet si vide."""
        if not self.reference:
            self.reference = generate_date_reference('BL', BonLivraison, self.date_bl)
        if not self.objet and self.dossier:
            self.objet = self.dossier.nom_projet
        super().save(*args, **kwargs)


# ============================================================
# 11. Modèle DetailBonLivraison
# ============================================================

class DetailBonLivraison(AuditableMixin, BaseModel):
    """
    Ligne de détail d'un Bon de Livraison.
    """

    bon_livraison = models.ForeignKey(
        BonLivraison,
        verbose_name=_('bon de livraison'),
        on_delete=models.CASCADE,
        related_name='details',
    )
    designation = models.CharField(
        _('désignation / livrable'),
        max_length=255,
    )
    ref_rapport = models.CharField(
        _('référence rapport'),
        max_length=100,
        blank=True,
    )
    quantite = models.DecimalField(
        _('quantité'),
        max_digits=10,
        decimal_places=2,
        default=1.00,
    )
    observations = models.CharField(
        _('observations'),
        max_length=255,
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('détail du bon de livraison')
        verbose_name_plural = _('détails du bon de livraison')

    def __str__(self):
        return f"{self.designation} (x{self.quantite})"


# ResultatBC déplacé vers l'application marches


# ============================================================
# 13. Modèle DetailDevis (Ligne de devis)
# ============================================================

class DetailDevis(AuditableMixin, BaseModel):
    """
    Ligne de détail d'un Devis (Bordereau des prix).
    """

    devis = models.ForeignKey(
        Devis,
        verbose_name=_('devis'),
        on_delete=models.CASCADE,
        related_name='details',
    )
    num_prix = models.CharField(
        _('N° prix'),
        max_length=50,
        blank=True,
    )
    designation = models.CharField(
        _('désignation'),
        max_length=255,
    )
    unite = models.CharField(
        _('unité'),
        max_length=50,
        blank=True,
    )
    quantite = models.DecimalField(
        _('quantité'),
        max_digits=10,
        decimal_places=2,
        default=1.00,
    )
    prix_unitaire = models.DecimalField(
        _('prix unitaire (H.T)'),
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    class Meta(BaseModel.Meta):
        verbose_name = _('détail du devis')
        verbose_name_plural = _('détails du devis')

    def __str__(self):
        return f"{self.designation} (x{self.quantite})"

    @property
    def prix_total(self):
        return self.quantite * self.prix_unitaire

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.devis.recalculate_totals()

    def delete(self, *args, **kwargs):
        devis = self.devis
        super().delete(*args, **kwargs)
        devis.recalculate_totals()
