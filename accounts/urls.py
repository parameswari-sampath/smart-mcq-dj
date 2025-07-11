from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Student access code join
    path('join-test/', views.join_test_session, name='join_test_session'),
    
    # Test details view
    path('test-details/<int:session_id>/', views.view_test_details, name='view_test_details'),
    
    # Test taking interface
    path('take-test/<int:attempt_id>/', views.take_test, name='take_test'),
    path('take-test/<int:attempt_id>/navigate/', views.navigate_question, name='navigate_question'),
    path('take-test/<int:attempt_id>/save-answer/', views.save_answer, name='save_answer'),
]