from django.urls import path
from . import views

app_name = 'gestion_droits_acces'

urlpatterns = [
    # Gestion des utilisateurs
    path('utilisateurs/', views.UserListView.as_view(), name='user_list'),
    path('utilisateurs/creer/', views.UserCreateView.as_view(), name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.UserUpdateView.as_view(), name='user_update'),
    path('utilisateurs/<int:pk>/toggle-actif/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),

    # Gestion des droits d'accès
    path('droits/', views.GestionDroitsView.as_view(), name='droits_matrix'),
    path('droits/toggle/', views.ToggleDroitView.as_view(), name='toggle_droit'),
]
