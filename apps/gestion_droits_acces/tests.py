from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.gestion_droits_acces.models import DroitAcces

User = get_user_model()


class DroitsAccesViewsTests(TestCase):
    """Tests pour la gestion des utilisateurs et les droits d'accès."""

    def setUp(self):
        self.client = Client()
        # Création du superuser (admin du système)
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            password='AdminPass123!',
            email='admin@labocos.ma',
        )
        self.admin_user.est_admin = True
        self.admin_user.save()

        # Création d'un utilisateur standard
        self.std_user = User.objects.create_user(
            username='std_user',
            password='UserPass123!',
            email='user@labocos.ma',
        )

        self.user_list_url = reverse('gestion_droits_acces:user_list')
        self.user_create_url = reverse('gestion_droits_acces:user_create')
        self.user_update_url = reverse('gestion_droits_acces:user_update', kwargs={'pk': self.std_user.pk})
        self.user_toggle_url = reverse('gestion_droits_acces:user_toggle_active', kwargs={'pk': self.std_user.pk})
        self.matrix_url = reverse('gestion_droits_acces:droits_matrix')
        self.toggle_droit_url = reverse('gestion_droits_acces:toggle_droit')

    def login_admin(self):
        self.client.login(username='admin_user', password='AdminPass123!')
        session = self.client.session
        session['selected_service'] = 'service_informatique'
        session.save()

    def login_std(self):
        self.client.login(username='std_user', password='UserPass123!')
        session = self.client.session
        session['selected_service'] = 'espace_user'
        session.save()

    def test_anonymous_access_denied(self):
        """Un utilisateur anonyme ou non admin ne peut pas accéder aux pages de gestion."""
        urls = [self.user_list_url, self.user_create_url, self.matrix_url]
        for url in urls:
            # Anonyme
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            
            # Non admin
            self.login_std()
            response_std = self.client.get(url)
            self.assertEqual(response_std.status_code, 302)
            self.client.logout()

    def test_admin_access_allowed(self):
        """L'admin ou le superuser accède avec succès."""
        self.login_admin()
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gestion_droits_acces/user_list.html')

    def test_create_user(self):
        """L'admin peut créer un nouvel utilisateur via le formulaire."""
        self.login_admin()
        
        post_data = {
            'username': 'new_user',
            'first_name': 'Nouveau',
            'last_name': 'User',
            'email': 'new@labocos.ma',
            'fonction': 'Qualiticien',
            'password1': 'NewPass123!',
            'password2': 'NewPass123!',
            'is_active': True,
        }
        response = self.client.post(self.user_create_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_update_user(self):
        """L'admin peut modifier les informations d'un utilisateur."""
        self.login_admin()
        
        post_data = {
            'username': 'std_user',
            'first_name': 'Modifie',
            'last_name': 'User',
            'email': 'user@labocos.ma',
            'fonction': 'Nouveau Poste',
            'is_active': True,
        }
        response = self.client.post(self.user_update_url, post_data)
        self.assertEqual(response.status_code, 302)
        
        self.std_user.refresh_from_db()
        self.assertEqual(self.std_user.first_name, 'Modifie')
        self.assertEqual(self.std_user.fonction, 'Nouveau Poste')

    def test_toggle_user_active(self):
        """L'admin peut désactiver ou réactiver un utilisateur."""
        self.login_admin()
        
        # Désactiver
        response = self.client.post(self.user_toggle_url)
        self.assertEqual(response.status_code, 302)
        self.std_user.refresh_from_db()
        self.assertFalse(self.std_user.is_active)
        
        # Réactiver
        response = self.client.post(self.user_toggle_url)
        self.assertEqual(response.status_code, 302)
        self.std_user.refresh_from_db()
        self.assertTrue(self.std_user.is_active)

    def test_toggle_droit_ajax(self):
        """Bascule des droits via POST AJAX crée et modifie les permissions."""
        self.login_admin()
        
        post_data = {
            'user_id': self.std_user.id,
            'service': 'service_administratif',
            'module': 'client',
            'permission': 'peut_voir',
        }
        # Première activation (n'existait pas)
        response = self.client.post(self.toggle_droit_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'value': True})
        
        droit = DroitAcces.objects.get(user=self.std_user, service='service_administratif', module='client')
        self.assertTrue(droit.peut_voir)
        
        # Désactivation
        response = self.client.post(self.toggle_droit_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True, 'value': False})
        
        droit.refresh_from_db()
        self.assertFalse(droit.peut_voir)

    def test_add_only_permission_flow(self):
        """Si un utilisateur n'a que le droit d'ajouter, il accède à la liste vide et peut ajouter."""
        # Configurer les droits : ajouter=True, voir=False
        DroitAcces.objects.create(
            user=self.std_user,
            service='service_administratif',
            module='client',
            peut_voir=False,
            peut_ajouter=True,
            peut_modifier=False,
            peut_annuler=False
        )

        self.login_std()
        
        # 1. Accès à la liste : doit renvoyer 200 (autorisé car peut_ajouter=True)
        list_url = reverse('commercial:client_list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        
        # 2. La liste d'objets dans le contexte doit être vide
        self.assertEqual(len(response.context['clients']), 0)
        
        # 3. Accès au formulaire d'ajout : doit être autorisé (200)
        create_url = reverse('commercial:client_create')
        response_create = self.client.get(create_url)
        self.assertEqual(response_create.status_code, 200)

