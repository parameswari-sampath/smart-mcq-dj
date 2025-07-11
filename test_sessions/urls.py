from django.urls import path
from . import views

app_name = 'test_sessions'

urlpatterns = [
    path('', views.session_list, name='session_list'),
    path('create/', views.session_create, name='session_create'),
    path('<int:pk>/', views.session_detail, name='session_detail'),
    path('<int:pk>/edit/', views.session_edit, name='session_edit'),
    path('<int:pk>/delete/', views.session_delete, name='session_delete'),
]