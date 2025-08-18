from django.contrib import admin
from .models import Project, UserProfile, Mail, Draft

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_projects']
    filter_horizontal = ['projects']
    
    def get_projects(self, obj):
        return ", ".join([p.name for p in obj.projects.all()])
    get_projects.short_description = 'Projects'

@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender', 'recipient', 'project', 'sent_at', 'is_read']
    list_filter = ['project', 'sent_at', 'is_read']
    search_fields = ['subject', 'body', 'sender__username', 'recipient__username']
    readonly_fields = ['sent_at']

@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ['subject', 'author', 'project', 'recipient', 'created_at', 'updated_at']
    list_filter = ['project', 'created_at', 'updated_at']
    search_fields = ['subject', 'body', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
