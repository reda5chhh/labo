from django.urls import path
from . import views

app_name = 'plannings_metrologie'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
