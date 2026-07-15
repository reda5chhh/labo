from django.urls import path
from . import views

app_name = 'etalonnage_interne'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
