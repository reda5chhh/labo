from django.urls import path
from . import views

app_name = 'gestion_ressources_humaines'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
