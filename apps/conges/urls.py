from django.urls import path
from . import views

app_name = 'conges'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
