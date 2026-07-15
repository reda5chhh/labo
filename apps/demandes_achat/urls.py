from django.urls import path
from . import views

app_name = 'demandes_achat'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
