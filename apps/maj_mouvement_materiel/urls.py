from django.urls import path
from . import views

app_name = 'maj_mouvement_materiel'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
