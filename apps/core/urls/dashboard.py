"""
LABO.COS App — URLs du dashboard et du profil.
"""
from django.urls import path
from apps.core.views import DashboardView, ProfileView

app_name = 'core'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('profil/', ProfileView.as_view(), name='profile'),
]
