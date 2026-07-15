from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.core.models import AuditLog
from apps.gestion_droits_acces.models import DroitAcces

User = get_user_model()

class AuditLogListViewTests(TestCase):
    def setUp(self):
        # Create different users
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            password='AdminPassword123!',
            email='admin@labocos.ma'
        )
        self.regular_user = User.objects.create_user(
            username='user_test',
            password='UserPassword123!',
            email='user@labocos.ma'
        )
        self.authorized_user = User.objects.create_user(
            username='auth_test',
            password='AuthPassword123!',
            email='auth@labocos.ma'
        )

        # Grant droit_acces to authorized user for 'suivi_modifications'
        DroitAcces.objects.create(
            user=self.authorized_user,
            service='service_informatique',
            module='suivi_modifications',
            peut_voir=True
        )

        # Create some audit logs
        AuditLog.objects.create(
            user=self.regular_user,
            action_type=AuditLog.ActionType.CREATE,
            model_name='Client',
            object_id=1,
            object_repr='Client A',
            ip_address='127.0.0.1'
        )
        AuditLog.objects.create(
            user=self.admin_user,
            action_type=AuditLog.ActionType.UPDATE,
            model_name='Devis',
            object_id=2,
            object_repr='Devis B',
            ip_address='192.168.1.1'
        )
        AuditLog.objects.create(
            user=self.regular_user,
            action_type=AuditLog.ActionType.CANCEL,
            model_name='Dossier',
            object_id=3,
            object_repr='Dossier C',
            ip_address='10.0.0.1'
        )

    def test_anonymous_redirected(self):
        url = reverse('suivi_modifications:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_unauthorized_user_blocked(self):
        self.client.login(username='user_test', password='UserPassword123!')
        url = reverse('suivi_modifications:dashboard')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Should redirect to core:dashboard
        self.assertEqual(response.url, reverse('core:dashboard'))

    def test_authorized_user_allowed(self):
        self.client.login(username='auth_test', password='AuthPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Suivi des modifications")
        # Should render logs list (at least our 3 custom logs, plus automatic ones like LOGIN)
        self.assertTrue(len(response.context['logs']) >= 3)

    def test_admin_user_allowed(self):
        self.client.login(username='admin_test', password='AdminPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['logs']) >= 3)

    def test_filtering_by_action_type(self):
        self.client.login(username='admin_test', password='AdminPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard') + '?action_type=CREATE'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # The CREATE action is only our mock log (User login is of type LOGIN)
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0].model_name, 'Client')

    def test_filtering_by_user(self):
        self.client.login(username='admin_test', password='AdminPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard') + f'?user_id={self.regular_user.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # regular_user did not log in during this client request, so only their 2 CREATE/CANCEL logs are returned
        self.assertEqual(len(response.context['logs']), 2)

    def test_filtering_by_model(self):
        self.client.login(username='admin_test', password='AdminPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard') + '?model_name=Devis'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0].model_name, 'Devis')

    def test_filtering_by_search_text(self):
        self.client.login(username='admin_test', password='AdminPassword123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()
        url = reverse('suivi_modifications:dashboard') + '?search=Dossier'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['logs']), 1)
        self.assertEqual(response.context['logs'][0].model_name, 'Dossier')
