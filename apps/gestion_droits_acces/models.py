"""
LABO.COS App — Modèle de gestion des droits d'accès.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


SERVICE_CHOICES = [
    ('service_administratif', _('Service Administratif')),
    ('service_technique',     _('Service Technique')),
    ('service_qualite',       _('Service Qualité')),
    ('service_metrologie',    _('Service Métrologie & Matériel')),
    ('espace_user',           _('Espace Utilisateur')),
    ('ged_archive',           _('GED Archive')),
    ('service_informatique',  _('Service Informatique')),
    ('parametrage',           _('Paramétrage')),
]

MODULE_CHOICES = [
    # Service Administratif
    # - Commercial
    ('client',                   _('Commercial — Clients')),
    ('revue_demande',            _('Commercial — Revue de la Demande')),
    ('devis',                    _('Commercial — Devis')),
    ('dossier',                  _('Commercial — Dossiers')),
    ('convention',               _('Commercial — Conventions')),
    ('bon_livraison',            _('Commercial — Bons de Livraison')),
    # - Marchés
    ('ao_soumission',            _('Marchés — AO Soumission')),
    ('ao_adjuge',                _('Marchés — AO Adjugé')),
    ('caution',                  _('Marchés — Cautions')),
    ('decompte',                 _('Marchés — Décomptes')),
    ('resultat_bc',              _('Marchés — Résultats BC')),
    # - Facturation & Comptabilité
    ('facture',                  _('Comptabilité — Factures')),
    ('encaissement',             _('Comptabilité — Encaissements')),
    ('recouvrement',             _('Comptabilité — Recouvrements')),
    ('mouvement_caisse',         _('Comptabilité — Caisse')),
    # - Achats & Logistique (aligned with base.html ?tab= query params)
    ('bci',                      _('Achats — BC Interne')),
    ('demande_prix',             _('Achats — Demande de prix')),
    ('prestataires_externes',    _('Achats — Sélection prestataires')),
    ('bons_commandes',           _('Achats — Bons de commande')),
    ('bons_reception',           _('Achats — Bons de réception')),
    ('evaluation_prestataires',  _('Achats — Évaluation prestataires')),
    ('prestataires_agrees',      _('Achats — Prestataires agréés')),
    ('cahier_charges',           _('Achats — Cahiers des charges')),
    # - Ressources Humaines (aligned with base.html ?tab= query params)
    ('personnel',                _('RH — Table personnel')),
    ('conges_rh',                _('RH — Table Congés')),
    ('attestations_rh',          _('RH — Table attestations')),
    ('stagiaires',               _('RH — Table des Stagiaires')),
    ('paie',                     _('RH — Table de Paie')),
    ('qualification',            _('RH — Table de Qualification')),

    # Service Technique
    # - Table des Réceptions (aligned with base.html ?tab= query params)
    ('reception_feuilles',       _('Réception — Feuilles')),
    ('reception_planning',       _('Réception — Planning')),
    # - Gestion Laboratoire (aligned with base.html ?tab= query params)
    ('preparation_bleu',         _('Labo — Préparation bleu')),
    ('solution_lavante',         _('Labo — Solution lavante')),
    ('suivi_balances',           _('Labo — Suivi des balances')),
    ('temperature_bassins',      _('Labo — Température Bassins')),
    ('planning_maintenance_labo',_('Labo — Planning maintenance')),
    ('fiche_maintenance',        _('Labo — Fiche maintenance')),
    ('gestion_consommable',      _('Labo — Gestion consommable')),
    ('conditions_ambiantes',     _('Labo — Conditions ambiantes')),
    ('controle_eau',             _('Labo — Contrôle eau distillée')),
    # - Formation & Qualification (aligned with base.html ?tab= query params)
    ('fiche_qualification',      _('Formation — Fiche de qualification')),
    ('feuilles_qualification',   _('Formation — Feuilles de Qualification')),

    # Service Qualité
    # - Gestion Documentaire (aligned with base.html ?tab= query params)
    ('suivi_docs',               _('Qualité — Suivi documents')),
    ('liste_suivi',              _('Qualité — Liste suivi docs')),
    ('revue_doc',                _('Qualité — Revue documentaire')),
    ('veille_normative',         _('Qualité — Veille Normative')),
    ('controle_enreg',           _('Qualité — Contrôle enregistrements')),
    ('abbreviations',            _('Qualité — Abréviations')),
    # - Fiche de Progrès
    ('fiche_progres',            _('Qualité — Fiche de Progrès')),

    # Service Métrologie
    ('inventaire_materiel',      _('Métrologie — Inventaire Matériel')),
    ('fiche_vie',                _('Métrologie — Fiche de Vie')),
    ('etalonnage_interne',       _('Métrologie — Étalonnage Internes')),
    ('maj_incertitude',          _('Métrologie — MAJ Incertitude')),
    ('maj_elements_etalonner',   _('Métrologie — MAJ Éléments à Étalonner')),
    ('maj_mouvement_materiel',   _('Métrologie — Mouvement Matériel')),
    ('planning_etalonnage',      _('Planning — Étalonnage')),
    ('planning_maintenance',     _('Planning — Maintenance')),
    ('moyens_mesure',            _('Capabilité — Moyens de Mesure')),
    ('balances',                 _('Capabilité — Balances')),
    ('exploitation_metrologique',_('Métrologie — Exploitation Métrologique')),
    ('verification_etuves',      _('Métrologie — Vérification Étuves')),
    ('donnees_balances',         _('Paramètres — Données Balances')),
    ('masses_etalons',           _('Paramètres — Données Masses Étalons')),
    ('donnees_materiel',         _('Paramètres — Données Matériel')),
    ('periodicite',              _('Paramètres — Périodicité')),
    ('instruction_etalonnage',   _('Paramètres — Instruction Étalonnage')),
    ('type_intervention',        _('Paramètres — Type Intervention')),
    ('accreditation',            _('Paramètres — Accréditation')),

    # Espace User
    ('conges',                   _("Espace User — Congés")),
    ('attestations',             _("Espace User — Attestations")),
    ('demandes_achat',           _("Espace User — Demandes d'Achat")),
    ('specimen_signature',       _("Espace User — Spécimen Signature")),

    # GED Archive
    ('archive_ged',              _('GED — Archive')),
    ('services_familles_ged',    _('GED — Services/Familles')),
    ('droits_ged',               _('GED — Droits d\'accès')),

    # Informatique
    ('suivi_modifications',      _('Informatique — Suivi Modifications')),
    ('gestion_droits_acces',     _('Informatique — Droits d\'accès')),
    ('donnees_informatique',     _('Informatique — Données')),

    # Paramétrage
    ('parametrage_general',      _('Paramétrage Général')),
]


class DroitAcces(models.Model):
    """
    Droits d'accès d'un utilisateur sur un service + module.
    4 permissions indépendantes : voir, ajouter, modifier, annuler.
    """
    user = models.ForeignKey(
        'core.User',
        verbose_name=_('utilisateur'),
        on_delete=models.CASCADE,
        related_name='droits_acces',
    )
    service = models.CharField(
        _('service'), max_length=50, choices=SERVICE_CHOICES,
    )
    module = models.CharField(
        _('module'), max_length=60, choices=MODULE_CHOICES,
    )
    peut_voir     = models.BooleanField(_('peut voir'),     default=False)
    peut_ajouter  = models.BooleanField(_('peut ajouter'),  default=False)
    peut_modifier = models.BooleanField(_('peut modifier'), default=False)
    peut_annuler  = models.BooleanField(_('peut annuler'),  default=False)

    class Meta:
        verbose_name        = _("droit d'accès")
        verbose_name_plural = _("droits d'accès")
        unique_together     = ('user', 'service', 'module')
        ordering            = ['user__username', 'service', 'module']

    def __str__(self):
        return f"{self.user.username} — {self.service}/{self.module}"
