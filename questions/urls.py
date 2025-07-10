from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('create/', views.question_create, name='question_create'),
    path('<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('<int:pk>/delete/', views.question_delete, name='question_delete'),
]