from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('create/', views.test_create, name='test_create'),
    path('<int:pk>/', views.test_detail, name='test_detail'),
    path('<int:pk>/edit/', views.test_edit, name='test_edit'),
    path('<int:pk>/delete/', views.test_delete, name='test_delete'),
]