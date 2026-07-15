from django.urls import path
from . import views

app_name = 'gestion_documentaire'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
