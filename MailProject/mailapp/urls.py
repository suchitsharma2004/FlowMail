from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent, name='sent'),
    path('compose/', views.compose, name='compose'),
    path('drafts/', views.drafts, name='drafts'),
    path('drafts/edit/<int:draft_id>/', views.edit_draft, name='edit_draft'),
    path('mail/<int:mail_id>/', views.read_mail, name='read_mail'),
    path('api/project-users/', views.get_project_users, name='get_project_users'),
    path('api/generate-ai-draft/', views.generate_ai_draft, name='generate_ai_draft'),
    path('projects/', views.manage_projects, name='manage_projects'),
    path('projects/create/', views.create_project, name='create_project'),
    path('health/', views.health_check, name='health_check'),  # Health check for debugging
    path('test/', views.simple_test, name='simple_test'),  # Simple test without database
    path('debug/user-data/', views.debug_user_data, name='debug_user_data'),  # Debug URL
    path('debug/project-data/', views.debug_project_data, name='debug_project_data'),  # Debug URL for project data
]
