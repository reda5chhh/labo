"""
LABO.COS App — Tests unitaires du module commercial.
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from apps.core.models import AuditLog
from apps.core.middleware import _thread_locals
from apps.commercial.models import Client, RevueDemande, Devis, Dossier, Convention, BonLivraison

User = get_user_model()


class MockRequest:
    """Mock minimal de requête HTTP pour simuler le thread local en test."""
    def __init__(self, user):
        self.user = user
        self.META = {'REMOTE_ADDR': '127.0.0.1'}


class CommercialModelsTestCase(TestCase):

    def setUp(self):
        # Création d'un utilisateur de test
        self.user = User.objects.create_user(
            username='chef_projet_test',
            password='Password123!',
            email='chef@labocos.ma',
            fonction='Chef de Projet'
        )
        
        # Injecter l'utilisateur dans le thread-local pour AuditableMixin
        _thread_locals.request = MockRequest(self.user)

        # Création d'un client de test
        self.client_test = Client.objects.create(
            nom="Client Test SARL",
            type_client=Client.ClientType.ENTREPRISE,
            ice="123456789012345",
            telephone="+212 5 22 00 00 00",
            adresse="Avenue des FAR, Casablanca"
        )

    def tearDown(self):
        # Nettoyage du thread local
        if hasattr(_thread_locals, 'request'):
            delattr(_thread_locals, 'request')

    def test_client_creation(self):
        """Vérifie que le client est créé avec les bonnes valeurs."""
        self.assertEqual(self.client_test.nom, "Client Test SARL")
        self.assertEqual(self.client_test.type_client, Client.ClientType.ENTREPRISE)
        self.assertTrue(self.client_test.active)
        
        # Vérifie qu'un AuditLog a été enregistré pour la création du client
        logs = AuditLog.objects.filter(model_name='Client', object_id=self.client_test.pk)
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().action_type, AuditLog.ActionType.CREATE)
        self.assertEqual(logs.first().user, self.user)

    def test_devis_calculations_and_reference(self):
        """Vérifie le calcul automatique du montant TTC, TVA et la référence unique du Devis."""
        devis = Devis.objects.create(
            client=self.client_test,
            objet="Essais géotechniques sur pont",
            montant_ht=10000.00,
            taux_tva=20.00
        )
        
        # Vérifie les calculs
        # 10000 * 20% = 2000 MAD de TVA
        self.assertEqual(devis.montant_tva, 2000.00)
        # 10000 + 2000 = 12000 MAD TTC
        self.assertEqual(devis.montant_ttc, 12000.00)
        
        # Vérifie la référence unique automatique
        current_year = timezone.now().year
        expected_ref = f"DEV-{current_year}-0001"
        self.assertEqual(devis.reference, expected_ref)

        # Création d'un second devis pour tester l'incrémentation
        devis_2 = Devis.objects.create(
            client=self.client_test,
            objet="Essais sur béton",
            montant_ht=5000.00,
            taux_tva=20.00
        )
        self.assertEqual(devis_2.reference, f"DEV-{current_year}-0002")

    def test_dossier_reference(self):
        """Vérifie la génération automatique de la référence du Dossier."""
        dossier = Dossier.objects.create(
            client=self.client_test,
            nom_projet="Chantier Port Casablanca",
            emplacement="Port de Casablanca",
            chef_projet=self.user
        )
        
        current_year = timezone.now().year
        self.assertEqual(dossier.reference, f"DOS-{current_year}-0001")

    def test_convention_reference(self):
        """Vérifie la génération automatique de la référence de la Convention."""
        convention = Convention.objects.create(
            client=self.client_test,
            objet="Accord cadre essais sols"
        )
        
        current_year = timezone.now().year
        self.assertEqual(convention.reference, f"CONV-{current_year}-0001")

    def test_bon_livraison_reference(self):
        """Vérifie la génération automatique de la référence du Bon de Livraison (BL)."""
        dossier = Dossier.objects.create(
            client=self.client_test,
            nom_projet="Chantier Résidence El Fath"
        )
        bl = BonLivraison.objects.create(
            dossier=dossier,
            destinataire="Mr. Samir Alaoui"
        )
        
        current_year = timezone.now().year
        self.assertEqual(bl.reference, f"BL-{current_year}-0001")
