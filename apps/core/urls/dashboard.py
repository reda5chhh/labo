"""
LABO.COS App — URLs du dashboard et du profil.
"""
from django.urls import path
from apps.core.views import DashboardView, ProfileView, SelectServiceView, GetEntityDataView

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('profil/', ProfileView.as_view(), name='profile'),
    path('select-service/', SelectServiceView.as_view(), name='select_service'),
    path('api/entity-info/<str:entity_type>/<int:entity_id>/', GetEntityDataView.as_view(), name='entity_info'),
]
