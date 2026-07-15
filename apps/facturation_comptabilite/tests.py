"""Tests unitaires pour le module Finance."""
import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.commercial.models import Client
from apps.table_receptions.models import Reception
from .models import Fournisseur, Facture, Encaissement, FactureFournisseur, Paiement, MouvementCaisse, Recouvrement

User = get_user_model()


class FinanceTestCase(TestCase):
    def setUp(self):
        # Création d'un utilisateur
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Création d'un client
        self.client_obj = Client.objects.create(
            nom="SOCIETE DE TEST MAROC",
            telephone="0522000000",
            created_by=self.user
        )

        # Création d'un fournisseur
        self.fournisseur = Fournisseur.objects.create(
            nom="FOURNISSEUR MATERIEL LABO",
            telephone="0522111111",
            created_by=self.user
        )

    def test_facture_creation_and_calculation(self):
        """Vérifie le calcul automatique de la TVA et du TTC et la génération de référence."""
        facture = Facture.objects.create(
            client=self.client_obj,
            date_facture=datetime.date.today(),
            date_echeance=datetime.date.today() + datetime.timedelta(days=30),
            montant_ht=1000.00,
            taux_tva=20.00,
            created_by=self.user
        )
        
        # Vérification des calculs
        self.assertEqual(facture.montant_tva, 200.00)
        self.assertEqual(facture.montant_ttc, 1200.00)
        
        # Vérification de la référence
        self.assertTrue(facture.reference.startswith('FAC-'))

    def test_encaissement_and_invoice_status(self):
        """Vérifie que l'enregistrement d'encaissements met à jour le statut de la facture."""
        facture = Facture.objects.create(
            client=self.client_obj,
            date_facture=datetime.date.today(),
            date_echeance=datetime.date.today() + datetime.timedelta(days=30),
            montant_ht=1000.00,
            taux_tva=20.00,
            created_by=self.user
        )
        
        # 1. Enregistrement d'un encaissement partiel
        enc1 = Encaissement.objects.create(
            facture=facture,
            date_encaissement=datetime.date.today(),
            montant=500.00,
            moyen_paiement=Encaissement.MoyenPaiement.CHEQUE,
            reference_transaction="CHQ-12345",
            created_by=self.user
        )
        
        facture.refresh_from_db()
        self.assertEqual(facture.statut, Facture.StatutFacture.PAYEE_PARTIEL)
        self.assertEqual(facture.solde, 700.00)

        # 2. Enregistrement du solde
        enc2 = Encaissement.objects.create(
            facture=facture,
            date_encaissement=datetime.date.today(),
            montant=700.00,
            moyen_paiement=Encaissement.MoyenPaiement.ESPECES,
            reference_transaction="CASH-001",
            created_by=self.user
        )
        
        facture.refresh_from_db()
        self.assertEqual(facture.statut, Facture.StatutFacture.PAYEE)
        self.assertEqual(facture.solde, 0.00)

        # Vérification qu'un mouvement de caisse d'entrée a été créé automatiquement pour l'espèces
        mvt = MouvementCaisse.objects.filter(encaissement=enc2).first()
        self.assertIsNotNone(mvt)
        self.assertEqual(mvt.type_mouvement, MouvementCaisse.TypeMouvement.ENTREE)
        self.assertEqual(mvt.montant, 700.00)

    def test_facture_fournisseur_and_payment(self):
        """Vérifie la facturation fournisseur et le paiement."""
        ff = FactureFournisseur.objects.create(
            reference_fournisseur="FAC-FR-998",
            fournisseur=self.fournisseur,
            date_facture=datetime.date.today(),
            date_echeance=datetime.date.today() + datetime.timedelta(days=30),
            montant_ht=5000.00,
            montant_tva=1000.00,
            montant_ttc=6000.00,
            created_by=self.user
        )

        self.assertTrue(ff.reference_interne.startswith('FF-'))
        self.assertEqual(ff.statut, FactureFournisseur.StatutFactureFournisseur.EN_ATTENTE)

        # Enregistrement du paiement complet en espèces
        paiement = Paiement.objects.create(
            facture_fournisseur=ff,
            date_paiement=datetime.date.today(),
            montant=6000.00,
            moyen_paiement=Paiement.MoyenPaiement.ESPECES,
            reference_transaction="CASH-OUT-01",
            created_by=self.user
        )

        ff.refresh_from_db()
        self.assertEqual(ff.statut, FactureFournisseur.StatutFactureFournisseur.PAYEE)
        self.assertEqual(ff.solde, 0.00)

        # Vérification qu'un mouvement de caisse de sortie a été créé automatiquement
        mvt = MouvementCaisse.objects.filter(paiement=paiement).first()
        self.assertIsNotNone(mvt)
        self.assertEqual(mvt.type_mouvement, MouvementCaisse.TypeMouvement.SORTIE)
        self.assertEqual(mvt.montant, 6000.00)
