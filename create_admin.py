"""Script de création du superuser admin initial pour LABO.COS App."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labocos.settings.local')
django.setup()

from apps.core.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@labocos.ma',
        password='Admin123!',
        first_name='Admin',
        last_name='Système',
        fonction='Administrateur LABO.COS',
        est_admin=True,
    )
    print('[OK] Superuser admin cree avec succes !')
    print('   Username : admin')
    print('   Password : Admin123!')
    print('   URL Admin: http://localhost:8000/admin/')
else:
    print('[INFO] Superuser admin existe deja.')
