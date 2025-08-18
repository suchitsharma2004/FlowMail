from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    projects = models.ManyToManyField(Project, related_name='members', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

class Mail(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_mails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_mails')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='mails')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"
    
    class Meta:
        ordering = ['-sent_at']

class Draft(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='drafts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='draft_recipients', null=True, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Draft by {self.author.username}: {self.subject or 'No subject'}"
    
    class Meta:
        ordering = ['-updated_at']
