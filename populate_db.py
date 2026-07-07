"""
Script to populate the LABO.COS database with realistic example data.
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labocos.settings.local')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.commercial.models import (
    Client, RevueDemande, Devis, DetailDevis, Dossier,
    Convention, AOSoumission, AOAdjuge, BonLivraison, Caution
)
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

User = get_user_model()

# ── 1. Superuser ──
admin = User.objects.create_superuser(
    username='admin',
    email='admin@labocos.ma',
    password='admin123',
    first_name='Mohamed',
    last_name='ALAMI',
)
print("✅ Superuser 'admin' created (password: admin123)")

# Additional users
u2 = User.objects.create_user(username='technicien1', password='tech123', first_name='Youssef', last_name='BENALI', email='youssef@labocos.ma')
u3 = User.objects.create_user(username='ingenieur1', password='ing123', first_name='Fatima', last_name='EL IDRISSI', email='fatima@labocos.ma')
u4 = User.objects.create_user(username='commercial1', password='com123', first_name='Ahmed', last_name='TAZI', email='ahmed@labocos.ma')
print("✅ 3 additional users created")

# ── 2. Clients ──
clients_data = [
    {
        'nom': 'ONCF - Office National des Chemins de Fer',
        'type_client': 'PUBLIC',
        'ice': '001234567000001',
        'rc': 'RC-RABAT-45678',
        'patente': '12345678',
        'if_fiscal': '98765432',
        'adresse': '8, Bis Rue Abderrahmane El Ghafiki, Agdal, Rabat',
        'telephone': '0537-774747',
        'email': 'contact@oncf.ma',
        'contact_nom': 'Ing. Karim BENNANI',
        'contact_telephone': '0661-234567',
        'contact_email': 'k.bennani@oncf.ma',
        'representant': 'M. Hassan CHRAIBI',
        'cin': 'BK456789',
    },
    {
        'nom': 'ADM - Autoroutes du Maroc',
        'type_client': 'PUBLIC',
        'ice': '001234567000002',
        'rc': 'RC-RABAT-12345',
        'patente': '87654321',
        'if_fiscal': '12345678',
        'adresse': 'Hay Riad, Rabat',
        'telephone': '0537-654321',
        'email': 'contact@adm.co.ma',
        'contact_nom': 'Ing. Salma OUAZZANI',
        'contact_telephone': '0662-345678',
        'contact_email': 's.ouazzani@adm.co.ma',
        'representant': 'M. Driss FILALI',
        'cin': 'BJ789012',
    },
    {
        'nom': 'SOMAGEC - Société Marocaine de Génie Civil',
        'type_client': 'PRIVE',
        'ice': '001234567000003',
        'rc': 'RC-CASA-67890',
        'patente': '11223344',
        'if_fiscal': '44332211',
        'adresse': 'Zone Industrielle, Ain Sebaa, Casablanca',
        'telephone': '0522-112233',
        'email': 'info@somagec.ma',
        'contact_nom': 'M. Omar CHERKAOUI',
        'contact_telephone': '0663-456789',
        'contact_email': 'o.cherkaoui@somagec.ma',
        'representant': 'M. Rachid FASSI FEHRI',
        'cin': 'BE345678',
    },
    {
        'nom': 'TGCC - Travaux Généraux de Construction de Casablanca',
        'type_client': 'PRIVE',
        'ice': '001234567000004',
        'rc': 'RC-CASA-99887',
        'patente': '55667788',
        'if_fiscal': '88776655',
        'adresse': 'Boulevard d\'Anfa, Casablanca',
        'telephone': '0522-998877',
        'email': 'contact@tgcc.ma',
        'contact_nom': 'Mme. Nadia AMRANI',
        'contact_telephone': '0664-567890',
        'contact_email': 'n.amrani@tgcc.ma',
    },
    {
        'nom': 'Ministère de l\'Équipement et de l\'Eau',
        'type_client': 'PUBLIC',
        'ice': '001234567000005',
        'adresse': 'Quartier Administratif, Rabat',
        'telephone': '0537-111222',
        'email': 'contact@equipement.gov.ma',
        'contact_nom': 'Ing. Mounia EL KHATIB',
        'contact_telephone': '0665-678901',
    },
]

clients = []
for cd in clients_data:
    c = Client.objects.create(**cd)
    clients.append(c)
print(f"✅ {len(clients)} clients created")

# ── 3. Revues de Demande ──
today = timezone.now().date()

rev1 = RevueDemande.objects.create(
    client=clients[0],
    date_demande=today - timedelta(days=30),
    objet='Essais géotechniques - Projet LGV Kénitra-Marrakech',
    ref_ao_bc='AO-2026/ONCF/LGV-03',
    lieu_execution='Tronçon Kénitra - Rabat',
    type_reception_demande='Au laboratoire',
    nature_prestation='Essais',
    type_revue='Initiale',
    etat_revue='Initiale',
    decision_labo='ACCORD',
    accord_client='ACCORD',
    q1_exigences='OUI', q2_methode='OUI', q3_incertitudes='NON',
    q4_echantillonnage='NA', q5_acheminement='OUI', q6_conservation='OUI',
    q7_soustraitance='NON', q8_transmission='OUI', q9_cooperation='OUI',
    q10_avis='NA', q11_declaration='NA', q12_equipements='OUI',
    q13_ressources='OUI', q14_methodes_choisies='OUI',
    discussion_client='Le client souhaite des rapports hebdomadaires. Délai de réalisation: 3 mois.',
    sortie_resultat='Proposition transmise au client',
    sortie_decision='OUI',
    validation_date=today - timedelta(days=28),
    validation_technique='Fatima EL IDRISSI',
)

rev2 = RevueDemande.objects.create(
    client=clients[1],
    date_demande=today - timedelta(days=15),
    objet='Contrôle qualité béton - Autoroute Tit Mellil',
    ref_ao_bc='BC-2026/ADM/045',
    lieu_execution='Autoroute Casablanca - Berrechid',
    type_reception_demande='Sur chantier',
    nature_prestation='Essais + Études',
    type_revue='Initiale',
    etat_revue='Initiale',
    decision_labo='ACCORD',
    accord_client='ATTENTE',
    q1_exigences='OUI', q2_methode='OUI', q3_incertitudes='OUI',
    q12_equipements='OUI', q13_ressources='OUI', q14_methodes_choisies='OUI',
    discussion_client='Demande de devis en urgence. Le client souhaite démarrer sous 10 jours.',
    sortie_resultat='Proposition transmise au client',
    sortie_decision='OUI',
    validation_date=today - timedelta(days=13),
    validation_technique='Mohamed ALAMI',
)

rev3 = RevueDemande.objects.create(
    client=clients[2],
    date_demande=today - timedelta(days=5),
    objet='Essais de sol - Projet résidentiel Bouskoura',
    lieu_execution='Bouskoura, Casablanca',
    type_reception_demande='Au laboratoire',
    nature_prestation='Essais',
    type_revue='Initiale',
    etat_revue='Initiale',
    decision_labo='ATTENTE',
    accord_client='ATTENTE',
    q1_exigences='OUI', q2_methode='OUI',
    q12_equipements='OUI', q13_ressources='OUI', q14_methodes_choisies='OUI',
)
print("✅ 3 revues de demande created")

# ── 4. Devis ──
dev1 = Devis.objects.create(
    reference='DEV-2026-001',
    client=clients[0],
    revue_demande=rev1,
    date_devis=today - timedelta(days=25),
    objet='Essais géotechniques LGV - Lot 1',
    montant_ht=Decimal('250000.00'),
    taux_tva=Decimal('20.00'),
    statut='ACCEPTE',
    conditions_reglement='30 jours fin de mois',
    validite_jours=90,
)

dev2 = Devis.objects.create(
    reference='DEV-2026-002',
    client=clients[1],
    revue_demande=rev2,
    date_devis=today - timedelta(days=10),
    objet='Contrôle qualité béton autoroute',
    montant_ht=Decimal('180000.00'),
    taux_tva=Decimal('20.00'),
    statut='ENVOYE',
    conditions_reglement='60 jours',
    validite_jours=60,
)

dev3 = Devis.objects.create(
    reference='DEV-2026-003',
    client=clients[2],
    date_devis=today - timedelta(days=3),
    objet='Essais de sol résidentiel Bouskoura',
    montant_ht=Decimal('45000.00'),
    taux_tva=Decimal('20.00'),
    statut='BROUILLON',
)
print("✅ 3 devis created")

# ── 5. Détails Devis (Bordereau des prix) ──
DetailDevis.objects.create(devis=dev1, num_prix='1.1', designation='Essai Proctor modifié', unite='U', quantite=20, prix_unitaire=Decimal('1500.00'))
DetailDevis.objects.create(devis=dev1, num_prix='1.2', designation='Essai CBR', unite='U', quantite=15, prix_unitaire=Decimal('2000.00'))
DetailDevis.objects.create(devis=dev1, num_prix='1.3', designation='Essai de plaque', unite='U', quantite=30, prix_unitaire=Decimal('3500.00'))
DetailDevis.objects.create(devis=dev1, num_prix='1.4', designation='Analyse granulométrique', unite='U', quantite=25, prix_unitaire=Decimal('800.00'))
DetailDevis.objects.create(devis=dev1, num_prix='1.5', designation='Limites d\'Atterberg', unite='U', quantite=25, prix_unitaire=Decimal('600.00'))

DetailDevis.objects.create(devis=dev2, num_prix='2.1', designation='Essai de compression béton (7j, 28j)', unite='U', quantite=100, prix_unitaire=Decimal('500.00'))
DetailDevis.objects.create(devis=dev2, num_prix='2.2', designation='Essai d\'affaissement (slump test)', unite='U', quantite=50, prix_unitaire=Decimal('300.00'))
DetailDevis.objects.create(devis=dev2, num_prix='2.3', designation='Prélèvement éprouvettes sur chantier', unite='Forf.', quantite=1, prix_unitaire=Decimal('25000.00'))
print("✅ Detail devis (bordereau des prix) created")

# ── 6. Dossiers ──
dos1 = Dossier.objects.create(
    reference='DOS-2026-001',
    client=clients[0],
    devis=dev1,
    nom_projet='LGV Kénitra-Marrakech - Lot Géotechnique',
    emplacement='Tronçon Kénitra - Rabat',
    date_ouverture=today - timedelta(days=20),
    chef_projet=u3,
    statut='EN_COURS',
    type_affaire='Marché',
    entreprise='ONCF',
    mode_reglement='HT',
    delai_paiement=30,
    echeance_facturation='Mensuelle',
)

dos2 = Dossier.objects.create(
    reference='DOS-2026-002',
    client=clients[3],
    nom_projet='Tour Mohammed VI - Contrôle béton',
    emplacement='Bab Lamrissa, Salé',
    date_ouverture=today - timedelta(days=90),
    chef_projet=u2,
    statut='EN_COURS',
)
print("✅ 2 dossiers created")

# ── 7. Conventions ──
conv1 = Convention.objects.create(
    reference='CONV-2026-001',
    client=clients[1],
    objet='Convention-cadre essais routiers 2026-2028',
    date_debut=today - timedelta(days=180),
    date_fin=today + timedelta(days=545),
    tarif_specifique='Tarifs négociés avec remise de 15% sur le barème standard.',
    statut='ACTIVE',
)
print("✅ 1 convention created")

# ── 8. Appels d'offres ──
ao1 = AOSoumission.objects.create(
    reference_ao='AO-2026-MEE-05',
    client=clients[4],
    objet='Contrôle qualité des travaux de la route nationale RN1 - Tronçon Agadir - Tiznit',
    date_limite=timezone.now() + timedelta(days=10),
    estimation_initiale=Decimal('800000.00'),
    montant_soumission=Decimal('750000.00'),
    statut='ADJUGE',
)

ao2 = AOSoumission.objects.create(
    reference_ao='BC-2026-ONCF-12',
    client=clients[0],
    objet='Essais de portance - Gare LGV de Kénitra',
    date_limite=timezone.now() + timedelta(days=15),
    estimation_initiale=Decimal('100000.00'),
    montant_soumission=Decimal('95000.00'),
    statut='PREPARATION',
)
print("✅ 2 AO soumissions created")

# ── 9. AO Adjugé ──
adj1 = AOAdjuge.objects.create(
    ao_soumission=ao1,
    date_adjudication=today - timedelta(days=5),
    montant_final=Decimal('750000.00'),
    caution_definitive_deposee=True,
    date_notification=today - timedelta(days=2),
    statut='EN_COURS',
)
print("✅ 1 AO adjugé created")

# ── 10. Cautions ──
Caution.objects.create(
    ao_adjuge=adj1,
    banque='Attijariwafa Bank',
    type_caution='DEFINITIVE',
    montant=Decimal('22500.00'),
    date_depot=today - timedelta(days=3),
    statut='DEPOSE',
)
print("✅ 1 caution created")

# ── 11. Bons de Livraison ──
bl1 = BonLivraison.objects.create(
    reference='BL-2026-001',
    dossier=dos1,
    date_bl=today - timedelta(days=7),
    destinataire='M. Hassan CHRAIBI',
    statut='ENVOYE',
    date_envoi=today - timedelta(days=7),
    envoi_par='Ahmed TAZI',
)
print("✅ 1 bon de livraison created")

print("\n" + "="*60)
print("🎉 DATABASE POPULATED SUCCESSFULLY!")
print("="*60)
print(f"   Superuser: admin / admin123")
print(f"   Users: technicien1/tech123, ingenieur1/ing123, commercial1/com123")
print(f"   Clients: {Client.objects.count()}")
print(f"   Revues: {RevueDemande.objects.count()}")
print(f"   Devis: {Devis.objects.count()}")
print(f"   Détails Devis: {DetailDevis.objects.count()}")
print(f"   Dossiers: {Dossier.objects.count()}")
print(f"   Conventions: {Convention.objects.count()}")
print(f"   AO Soumissions: {AOSoumission.objects.count()}")
print(f"   AO Adjugés: {AOAdjuge.objects.count()}")
print(f"   Cautions: {Caution.objects.count()}")
print(f"   Bons de Livraison: {BonLivraison.objects.count()}")
