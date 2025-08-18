from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Mail, Draft

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    # Project selection field
    project_choice = forms.ChoiceField(
        choices=[('new', 'Create New Project'), ('existing', 'Join Existing Project')],
        widget=forms.RadioSelect,
        initial='existing'
    )
    
    new_project_name = forms.CharField(
        max_length=100, 
        required=False,
        help_text="Enter project name if creating a new project"
    )
    
    new_project_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional project description"
    )
    
    existing_project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="Select a project to join",
        help_text="Choose an existing project to join"
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Special handling for radio buttons
        self.fields['project_choice'].widget.attrs['class'] = 'form-check-input'
    
    def clean(self):
        cleaned_data = super().clean()
        project_choice = cleaned_data.get('project_choice')
        new_project_name = cleaned_data.get('new_project_name')
        existing_project = cleaned_data.get('existing_project')
        
        if project_choice == 'new' and not new_project_name:
            raise forms.ValidationError("Project name is required when creating a new project.")
        
        if project_choice == 'existing' and not existing_project:
            raise forms.ValidationError("Please select an existing project to join.")
        
        return cleaned_data

class ComposeMailForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        empty_label="Select Project"
    )
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select Recipient"
    )
    
    class Meta:
        model = Mail
        fields = ['project', 'recipient', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter your message'}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            # Get projects the user is a member of
            if hasattr(user, 'userprofile'):
                user_projects = user.userprofile.projects.all()
            else:
                user_projects = Project.objects.none()
            
            self.fields['project'].queryset = user_projects
            
            # If there's data (POST request), populate recipient queryset based on selected project
            if self.data and 'project' in self.data and self.data.get('project'):
                try:
                    project_id = int(self.data.get('project'))
                    project = Project.objects.get(id=project_id)
                    recipients = User.objects.filter(
                        userprofile__projects=project
                    ).exclude(id=user.id)  # Exclude sender from recipients
                    self.fields['recipient'].queryset = recipients
                except (ValueError, TypeError, Project.DoesNotExist):
                    self.fields['recipient'].queryset = User.objects.none()
            else:
                # Initially empty recipient field - will be populated via AJAX based on project selection
                self.fields['recipient'].queryset = User.objects.none()
        
        # Add Bootstrap classes and ensure form rendering works
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
            })
            if field_name == 'project':
                field.widget.attrs.update({
                    'class': 'form-control form-select',
                    'id': 'id_project'
                })

class DraftForm(forms.ModelForm):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        empty_label="Select Project"
    )
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select Recipient",
        required=False
    )
    
    class Meta:
        model = Draft
        fields = ['project', 'recipient', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter your message'}),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        if user:
            # Get projects the user is a member of
            user_projects = user.userprofile.projects.all() if hasattr(user, 'userprofile') else Project.objects.none()
            self.fields['project'].queryset = user_projects
            
            # If there's data (POST request), populate recipient queryset based on selected project
            if hasattr(self, 'data') and self.data and 'project' in self.data:
                try:
                    project_id = int(self.data.get('project'))
                    project = Project.objects.get(id=project_id)
                    recipients = User.objects.filter(
                        userprofile__projects=project
                    ).exclude(id=user.id)  # Exclude sender from recipients
                    self.fields['recipient'].queryset = recipients
                except (ValueError, TypeError, Project.DoesNotExist):
                    self.fields['recipient'].queryset = User.objects.none()
            else:
                # Initially empty recipient field - will be populated via AJAX based on project selection
                self.fields['recipient'].queryset = User.objects.none()
