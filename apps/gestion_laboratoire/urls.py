from django.urls import path
from . import views

app_name = 'gestion_laboratoire'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
