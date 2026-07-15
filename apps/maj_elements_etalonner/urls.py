from django.urls import path
from . import views

app_name = 'maj_elements_etalonner'

urlpatterns = [
    path('', views.PlaceholderDashboardView.as_view(), name='dashboard'),
]
