from django.urls import path
from . import views

app_name = 'inventaire_materiel'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
