from django.urls import path
from . import views

app_name = 'fiche_progres'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
