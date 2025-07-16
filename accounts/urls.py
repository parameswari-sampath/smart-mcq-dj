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
    path('take-test/<int:attempt_id>/submit/', views.submit_test, name='submit_test'),
    
    # Test results
    path('test-results/', views.test_results, name='test_results'),
    path('test-results/<int:attempt_id>/', views.result_detail, name='result_detail'),
    
    # Teacher result views (v1.4)
    path('teacher-results/<int:session_id>/', views.teacher_test_results, name='teacher_test_results'),
    path('teacher-results/<int:session_id>/student/<int:attempt_id>/', views.teacher_student_detail, name='teacher_student_detail'),
    
    # Result release management (v1.4.1)
    path('teacher-results/<int:session_id>/release-management/', views.teacher_result_release_management, name='teacher_result_release_management'),
    path('teacher-results/<int:session_id>/release/<int:attempt_id>/', views.individual_result_release, name='individual_result_release'),
    
    # CSRF token refresh for long-running sessions
    path('refresh-csrf-token/', views.refresh_csrf_token, name='refresh_csrf_token'),
]