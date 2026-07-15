"""
LABO.COS App — URLs du module technique.
"""
from django.urls import path
from . import views

app_name = 'technique'

urlpatterns = [
    # Réceptions
    path('receptions/', views.ReceptionListView.as_view(), name='reception_list'),
    path('receptions/<int:pk>/', views.ReceptionDetailView.as_view(), name='reception_detail'),
    path('receptions/creer/', views.ReceptionCreateView.as_view(), name='reception_create'),
    path('receptions/<int:pk>/modifier/', views.ReceptionUpdateView.as_view(), name='reception_update'),
    path('receptions/<int:pk>/supprimer/', views.ReceptionDeleteView.as_view(), name='reception_delete'),
]
