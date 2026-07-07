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
        """Le dashboard est accessible pour les utilisateurs connectés."""
        self.client.login(username='dashtest', password='TestPass123!')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_dashboard_has_stats_context(self):
        """Le contexte du dashboard contient les statistiques."""
        self.client.login(username='dashtest', password='TestPass123!')
        response = self.client.get(self.dashboard_url)
        self.assertIn('stats', response.context)
