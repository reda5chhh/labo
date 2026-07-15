"""
Script to populate the invoicing and billing database with rich example data.
"""
import os, sys, django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labocos.settings.local')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from apps.commercial.models import Client, Devis, Dossier
from apps.facturation_comptabilite.models import Facture, LigneFacture, Encaissement

User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()

if not admin:
    print("Please run populate_db.py first to create the admin user.")
    sys.exit(1)

# Retrieve existing clients, devis, dossiers
clients = list(Client.objects.all())
devis = list(Devis.objects.all())
dossiers = list(Dossier.objects.all())

if not clients:
    print("Please run populate_db.py first to create clients, devis, and dossiers.")
    sys.exit(1)

print("Starting factures database seeding...")

# Clear existing factures and line items to prevent duplicates
Facture.objects.all().delete()
print("Cleared existing factures.")

# 1. Facture 1: Soldée (fully paid)
f1 = Facture.objects.create(
    reference="FAC-2026-0001",
    client=clients[0],
    devis=devis[0] if len(devis) > 0 else None,
    dossier=dossiers[0] if len(dossiers) > 0 else None,
    date_facture=date(2026, 6, 1),
    delai=30,
    bc="BC-ONCF-998",
    type_facture="DIRECTE",
    avec_ras="Non",
    projet="Projet LGV Kénitra-Marrakech - Lot Géotechnique",
    commentaire="Facture réglée par virement.",
    created_by=admin,
    envoye=True,
    envoye_par=admin,
    date_envoi=date(2026, 6, 2),
    accuse=True,
    date_accuse=date(2026, 6, 4),
    validee_par_signature=True,
    difficulte_recouvrement="RECOUVRABLE"
)

LigneFacture.objects.create(facture=f1, num_prix="1.1", designation="Essai Proctor modifié", unite="U", quantite=10, prix_unitaire=Decimal("1500.00"), created_by=admin)
LigneFacture.objects.create(facture=f1, num_prix="1.2", designation="Essai CBR", unite="U", quantite=5, prix_unitaire=Decimal("2000.00"), created_by=admin)
LigneFacture.objects.create(facture=f1, num_prix="1.3", designation="Essai de plaque", unite="U", quantite=8, prix_unitaire=Decimal("3500.00"), created_by=admin)

f1.refresh_from_db()
Encaissement.objects.create(
    facture=f1,
    date_encaissement=date(2026, 6, 25),
    montant=f1.montant_ttc,
    moyen_paiement="VIREMENT",
    reference_transaction="VIR-ONCF-1122",
    encaisse=True,
    created_by=admin
)
print("✅ Facture 1 created: FAC-2026-0001 (Soldée)")

# 2. Facture 2: Payée Partiellement
f2 = Facture.objects.create(
    reference="FAC-2026-0002",
    client=clients[1],
    date_facture=date(2026, 6, 15),
    delai=30,
    bc="BC-ADM-554",
    type_facture="SITUATION",
    avec_ras="OUI_10",
    projet="Autoroute Tit Mellil - Lot Béton",
    commentaire="En attente de paiement du solde.",
    created_by=admin,
    envoye=True,
    envoye_par=admin,
    date_envoi=date(2026, 6, 16),
    accuse=True,
    date_accuse=date(2026, 6, 18),
    validee_par_signature=True,
    difficulte_recouvrement="DIFFICILE"
)

LigneFacture.objects.create(facture=f2, num_prix="2.1", designation="Essai de compression béton (7j, 28j)", unite="U", quantite=50, prix_unitaire=Decimal("500.00"), created_by=admin)
LigneFacture.objects.create(facture=f2, num_prix="2.2", designation="Prélèvement éprouvettes sur chantier", unite="Forf.", quantite=1, prix_unitaire=Decimal("12000.00"), created_by=admin)

f2.refresh_from_db()
# Partial payment of 20000.00 DH
Encaissement.objects.create(
    facture=f2,
    date_encaissement=date(2026, 7, 5),
    montant=Decimal("20000.00"),
    moyen_paiement="CHEQUE",
    reference_transaction="CHQ-ADM-8874",
    encaisse=True,
    created_by=admin
)
print("✅ Facture 2 created: FAC-2026-0002 (Partielle)")

# 3. Facture 3: Non Envoyée / Non payée
f3 = Facture.objects.create(
    reference="FAC-2026-0003",
    client=clients[2],
    date_facture=date(2026, 7, 10),
    delai=45,
    bc="BC-SOMAGEC-112",
    type_facture="DIRECTE",
    avec_ras="Non",
    projet="Essais de sol résidentiel Bouskoura",
    commentaire="Brouillon prêt à l'envoi.",
    created_by=admin,
    envoye=False,
    accuse=False,
    validee_par_signature=False,
    difficulte_recouvrement="RECOUVRABLE"
)

LigneFacture.objects.create(facture=f3, num_prix="3.1", designation="Analyse granulométrique", unite="U", quantite=20, prix_unitaire=Decimal("800.00"), created_by=admin)
LigneFacture.objects.create(facture=f3, num_prix="3.2", designation="Limites d'Atterberg", unite="U", quantite=15, prix_unitaire=Decimal("600.00"), created_by=admin)

f3.refresh_from_db()
print("✅ Facture 3 created: FAC-2026-0003 (En cours / Non envoyée)")

# 4. Facture 4: En Retard / Non Payée / Difficile
f4 = Facture.objects.create(
    reference="FAC-2026-0004",
    client=clients[3] if len(clients) > 3 else clients[0],
    date_facture=date(2026, 5, 5),
    delai=30, # Due on 2026-06-04, which is in retard on 2026-07-15
    bc="BC-TGCC-009",
    type_facture="DIRECTE",
    avec_ras="Non",
    projet="Tour Mohammed VI - Prestations Béton",
    commentaire="Client contacté à plusieurs reprises par le service recouvrement.",
    created_by=admin,
    envoye=True,
    envoye_par=admin,
    date_envoi=date(2026, 5, 6),
    accuse=True,
    date_accuse=date(2026, 5, 8),
    validee_par_signature=True,
    difficulte_recouvrement="DIFFICILE"
)

LigneFacture.objects.create(facture=f4, num_prix="4.1", designation="Sondage carotté rotatif", unite="m", quantite=35, prix_unitaire=Decimal("1200.00"), created_by=admin)
LigneFacture.objects.create(facture=f4, num_prix="4.2", designation="Rapport d'étude de sol", unite="Forf.", quantite=1, prix_unitaire=Decimal("15000.00"), created_by=admin)

f4.refresh_from_db()
print("✅ Facture 4 created: FAC-2026-0004 (En retard / Difficile)")

print("\nSeeding finished! Database is ready with 4 rich invoices and payment logs.")
