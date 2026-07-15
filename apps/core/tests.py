"""
LABO.COS App — Tests unitaires pour l'application core.

Couvre :
- Création du modèle User personnalisé
- Création des entrées AuditLog
- AuditableMixin (auto-création AuditLog)
- Vue de connexion / déconnexion
- Middleware AuditLogMiddleware
"""
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AuditLog
from apps.gestion_droits_acces.models import DroitAcces

User = get_user_model()


class UserModelTests(TestCase):
    """Tests du modèle User personnalisé."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            first_name='Ahmed',
            last_name='Benali',
            fonction='Technicien',
        )

    def test_user_creation(self):
        """Un User peut être créé avec les champs personnalisés."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.fonction, 'Technicien')
        self.assertFalse(self.user.est_admin)

    def test_nom_complet_property(self):
        """La propriété nom_complet retourne prénom + nom."""
        self.assertEqual(self.user.nom_complet, 'Ahmed Benali')

    def test_nom_complet_sans_nom(self):
        """Sans nom complet, retourne le username."""
        user = User.objects.create_user(username='noname', password='pass123')
        self.assertEqual(user.nom_complet, 'noname')

    def test_str_representation(self):
        """__str__ retourne le nom complet."""
        self.assertEqual(str(self.user), 'Ahmed Benali')

    def test_est_admin_default_false(self):
        """est_admin doit être False par défaut."""
        self.assertFalse(self.user.est_admin)


class AuditLogModelTests(TestCase):
    """Tests du modèle AuditLog."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='audituser', password='TestPass123!'
        )

    def test_log_creation(self):
        """La méthode log() crée une entrée AuditLog."""
        log = AuditLog.log(
            user=self.user,
            action_type=AuditLog.ActionType.CREATE,
            model_name='TestModel',
            object_id=42,
            object_repr='Test Object',
        )
        self.assertIsNotNone(log.pk)
        self.assertEqual(log.action_type, 'CREATE')
        self.assertEqual(log.model_name, 'TestModel')
        self.assertEqual(log.user, self.user)

    def test_log_without_user(self):
        """Un AuditLog peut être créé sans utilisateur (connexion échouée)."""
        log = AuditLog.log(
            user=None,
            action_type=AuditLog.ActionType.LOGIN,
            object_repr='Tentative de connexion échouée',
        )
        self.assertIsNone(log.user)

    def test_log_str_representation(self):
        """__str__ retourne une représentation lisible."""
        log = AuditLog.log(
            user=self.user,
            action_type=AuditLog.ActionType.UPDATE,
            model_name='Facture',
            object_id=1,
        )
        self.assertIn('Modification', str(log))
        self.assertIn('Facture', str(log))


class LoginViewTests(TestCase):
    """Tests de la vue de connexion."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='logintest',
            password='TestPass123!',
        )
        # Accorder l'accès au service administratif
        DroitAcces.objects.create(
            user=self.user,
            service='service_administratif',
            module='client',
            peut_voir=True
        )
        self.login_url = reverse('auth:login')

    def test_login_page_accessible(self):
        """La page de connexion est accessible sans authentification."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_success(self):
        """Connexion réussie avec identifiants corrects."""
        response = self.client.post(self.login_url, {
            'username': 'logintest',
            'password': 'TestPass123!',
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_failure(self):
        """Connexion échouée avec mauvais mot de passe."""
        response = self.client.post(self.login_url, {
            'username': 'logintest',
            'password': 'wrong_password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_login_creates_audit_log(self):
        """Une connexion réussie crée une entrée AuditLog de type LOGIN."""
        initial_count = AuditLog.objects.filter(
            action_type=AuditLog.ActionType.LOGIN
        ).count()
        self.client.post(self.login_url, {
            'username': 'logintest',
            'password': 'TestPass123!',
        })
        new_count = AuditLog.objects.filter(
            action_type=AuditLog.ActionType.LOGIN
        ).count()
        self.assertGreater(new_count, initial_count)


class DashboardViewTests(TestCase):
    """Tests de la vue du tableau de bord."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashtest',
            password='TestPass123!',
        )
        self.dashboard_url = reverse('core:dashboard')

    def test_dashboard_requires_login(self):
        """Le dashboard nécessite d'être connecté."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response['Location'])

    def test_dashboard_accessible_when_logged_in(self):
        """Le dashboard est accessible pour les utilisateurs connectés ayant choisi un service."""
        self.client.login(username='dashtest', password='TestPass123!')
        
        # Choisir un service dans la session
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_dashboard_has_stats_context(self):
        """Le contexte du dashboard contient les statistiques."""
        self.client.login(username='dashtest', password='TestPass123!')
        
        # Choisir un service dans la session
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        
        response = self.client.get(self.dashboard_url)
        self.assertIn('stats', response.context)


class ServiceSelectionTests(TestCase):
    """Tests du processus de sélection de service."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='serviceuser',
            password='TestPass123!',
        )
        DroitAcces.objects.create(
            user=self.user,
            service='service_administratif',
            module='client',
            peut_voir=True
        )
        self.select_url = reverse('core:select_service')
        self.dashboard_url = reverse('core:dashboard')

    def test_redirect_to_select_service_after_login(self):
        """Un utilisateur connecté sans service est redirigé vers la page de choix de service."""
        self.client.login(username='serviceuser', password='TestPass123!')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.select_url, response['Location'])

    def test_select_service_page_accessible(self):
        """La page de choix de service est accessible pour un utilisateur connecté."""
        self.client.login(username='serviceuser', password='TestPass123!')
        response = self.client.get(self.select_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/select_service.html')

    def test_select_service_saves_in_session(self):
        """Choisir un service valide l'enregistre en session et redirige vers le dashboard."""
        self.client.login(username='serviceuser', password='TestPass123!')
        response = self.client.post(self.select_url, {'service': 'service_administratif'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['selected_service'], 'service_administratif')
        
        # Maintenant le dashboard est accessible
        response2 = self.client.get(self.dashboard_url)
        self.assertEqual(response2.status_code, 200)

    def test_select_service_admin_only_restricted(self):
        """Un utilisateur non-admin ne peut pas sélectionner de service admin."""
        self.client.login(username='serviceuser', password='TestPass123!')
        response = self.client.post(self.select_url, {'service': 'service_informatique'})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('selected_service', self.client.session)


class GetEntityDataViewTests(TestCase):
    """Tests pour l'API JSON GetEntityDataView."""

    def setUp(self):
        from django.test import Client as DjangoClient
        self.client = DjangoClient()
        self.user = User.objects.create_user(
            username='apitestuser',
            password='TestPass123!',
        )
        # Create test models
        from apps.commercial.models import Client as SystemClient, Devis, Dossier
        from apps.marches.models import AOSoumission
        from django.utils import timezone
        
        self.system_client = SystemClient.objects.create(
            nom='Client Test',
            representant='Jean Dupont',
            adresse='123 Rue de la Gare',
            telephone='0600000000',
            email='client@test.com',
            ice='123456789000012',
        )
        
        self.devis = Devis.objects.create(
            client=self.system_client,
            objet='Devis Test',
            montant_ht=1000.00,
            montant_ttc=1200.00,
        )
        
        self.dossier = Dossier.objects.create(
            client=self.system_client,
            nom_projet='Projet Test',
        )
        
        self.ao = AOSoumission.objects.create(
            reference_ao='AO-999',
            client=self.system_client,
            objet='Marche Test',
            estimation_initiale=50000.00,
            montant_soumission=45000.00,
            date_limite=timezone.now(),
        )

    def test_endpoint_requires_login(self):
        """L'accès à l'API requiert d'être connecté."""
        url = reverse('core:entity_info', kwargs={'entity_type': 'client', 'entity_id': self.system_client.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_get_client_info(self):
        """Récupérer les informations d'un Client."""
        self.client.login(username='apitestuser', password='TestPass123!')
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        url = reverse('core:entity_info', kwargs={'entity_type': 'client', 'entity_id': self.system_client.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['nom'], 'Client Test')
        self.assertEqual(data['representant'], 'Jean Dupont')
        self.assertEqual(data['telephone'], '0600000000')

    def test_get_devis_info(self):
        """Récupérer les informations d'un Devis."""
        self.client.login(username='apitestuser', password='TestPass123!')
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        url = reverse('core:entity_info', kwargs={'entity_type': 'devis', 'entity_id': self.devis.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['client_id'], self.system_client.pk)
        self.assertEqual(data['objet'], 'Devis Test')
        self.assertEqual(data['montant_ht'], '1000.00')

    def test_get_dossier_info(self):
        """Récupérer les informations d'un Dossier."""
        self.client.login(username='apitestuser', password='TestPass123!')
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        url = reverse('core:entity_info', kwargs={'entity_type': 'dossier', 'entity_id': self.dossier.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['client_id'], self.system_client.pk)
        self.assertEqual(data['nom_projet'], 'Projet Test')

    def test_get_ao_info(self):
        """Récupérer les informations d'un AO."""
        self.client.login(username='apitestuser', password='TestPass123!')
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        url = reverse('core:entity_info', kwargs={'entity_type': 'ao', 'entity_id': self.ao.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['client_id'], self.system_client.pk)
        self.assertEqual(data['maitre_ouvrage'], 'Client Test')
        self.assertEqual(data['objet'], 'Marche Test')
        self.assertEqual(data['montant_soumission'], '45000.00')

    def test_invalid_entity_type(self):
        """Une entité inconnue retourne une erreur 400."""
        self.client.login(username='apitestuser', password='TestPass123!')
        session = self.client.session
        session['selected_service'] = 'service_administratif'
        session.save()
        url = reverse('core:entity_info', kwargs={'entity_type': 'unknown', 'entity_id': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)


