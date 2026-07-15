from django.urls import path
from . import views

app_name = 'donnees_informatique'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
