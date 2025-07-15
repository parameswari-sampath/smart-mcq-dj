from django.urls import path
from . import views

app_name = 'server_status'

urlpatterns = [
    path('', views.server_status, name='status'),
    path('health/', views.health_check, name='health'),
]