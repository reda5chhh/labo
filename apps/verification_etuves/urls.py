from django.urls import path
from . import views

app_name = 'verification_etuves'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
