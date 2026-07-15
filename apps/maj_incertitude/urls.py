from django.urls import path
from . import views

app_name = 'maj_incertitude'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
