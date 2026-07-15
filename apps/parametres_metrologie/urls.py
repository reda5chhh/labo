from django.urls import path
from . import views

app_name = 'parametres_metrologie'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
