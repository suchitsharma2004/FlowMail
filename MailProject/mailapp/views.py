from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import google.generativeai as genai
from .models import Project, UserProfile, Mail, Draft
from .forms import CustomUserCreationForm, ComposeMailForm, DraftForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Create the user
                user = form.save()
                
                # Create UserProfile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Handle project selection
                project_choice = form.cleaned_data['project_choice']
                
                if project_choice == 'new':
                    # Create new project
                    project = Project.objects.create(
                        name=form.cleaned_data['new_project_name'],
                        description=form.cleaned_data.get('new_project_description', ''),
                        created_by=user
                    )
                    profile.projects.add(project)
                else:
                    # Join existing project
                    project = form.cleaned_data.get('existing_project')
                    if project:
                        profile.projects.add(project)
                    else:
                        # Create a default project if none selected
                        project = Project.objects.create(
                            name=f"{user.username}'s Project",
                            description="Default project",
                            created_by=user
                        )
                        profile.projects.add(project)
                
                # Authenticate and login
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'Account created successfully! Welcome to {project.name}!')
                    return redirect('inbox')
                else:
                    messages.error(request, 'Authentication failed after registration.')
                    
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                # Delete the user if it was created but something else failed
                if 'user' in locals():
                    try:
                        user.delete()
                    except:
                        pass
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'mailapp/register.html', {'form': form})

@login_required
def inbox(request):
    try:
        # Ensure user has a UserProfile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get user's projects
        user_projects = profile.projects.all()
        
        # If user has no projects, create a default one
        if not user_projects.exists():
            default_project = Project.objects.create(
                name=f"{request.user.username}'s Project",
                description="Default project",
                created_by=request.user
            )
            profile.projects.add(default_project)
            user_projects = profile.projects.all()
        
        # Get project filter from query params
        project_filter = request.GET.get('project', '').strip()
        
        # Get mails for the user
        mails = Mail.objects.filter(recipient=request.user).order_by('-sent_at')
        
        # Handle project filtering
        if project_filter and project_filter.lower() != 'none' and project_filter != '':
            try:
                project_filter = int(project_filter)
                mails = mails.filter(project_id=project_filter)
            except (ValueError, TypeError):
                project_filter = ''
        else:
            project_filter = ''
    
    except Exception as e:
        messages.error(request, f'Error loading inbox: {str(e)}')
        user_projects = []
        mails = Mail.objects.none()
        project_filter = ''
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query and search_query.lower() != 'none':
        mails = mails.filter(
            Q(subject__icontains=search_query) |
            Q(body__icontains=search_query) |
            Q(sender__username__icontains=search_query) |
            Q(sender__first_name__icontains=search_query) |
            Q(sender__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(mails, 10)  # Show 10 mails per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_projects': user_projects,
        'current_project': str(project_filter) if project_filter else '',
        'search_query': search_query if search_query.lower() != 'none' else '',
    }
    
    return render(request, 'mailapp/inbox.html', context)

@login_required
def sent(request):
    """View to display sent mails"""
    # Get user's projects
    user_projects = request.user.userprofile.projects.all() if hasattr(request.user, 'userprofile') else []
    
    # Get project filter from query params
    project_filter = request.GET.get('project', '').strip()
    
    # Get mails sent by the user
    sent_mails = Mail.objects.filter(sender=request.user).order_by('-sent_at')
    
    # Handle project filtering
    if project_filter and project_filter.lower() != 'none' and project_filter != '':
        try:
            project_filter = int(project_filter)
            sent_mails = sent_mails.filter(project_id=project_filter)
        except (ValueError, TypeError):
            project_filter = ''
    else:
        project_filter = ''
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query and search_query.lower() != 'none':
        sent_mails = sent_mails.filter(
            Q(subject__icontains=search_query) |
            Q(body__icontains=search_query) |
            Q(recipient__username__icontains=search_query) |
            Q(recipient__first_name__icontains=search_query) |
            Q(recipient__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(sent_mails, 10)  # Show 10 mails per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'user_projects': user_projects,
        'current_project': str(project_filter) if project_filter else '',
        'search_query': search_query if search_query.lower() != 'none' else '',
    }
    
    return render(request, 'mailapp/sent.html', context)

@login_required
def compose(request):
    # Ensure user has a profile
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)
        messages.warning(request, 'User profile created. Please join a project first.')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send':
            form = ComposeMailForm(user=request.user, data=request.POST)
            if form.is_valid():
                mail = form.save(commit=False)
                mail.sender = request.user
                mail.save()
                messages.success(request, 'Mail sent successfully!')
                return redirect('inbox')
            # If form is invalid, it will fall through to render with errors
        
        elif action == 'draft':
            # Save as draft
            draft_form = DraftForm(user=request.user, data=request.POST)
            if draft_form.is_valid():
                draft = draft_form.save(commit=False)
                draft.author = request.user
                draft.save()
                messages.success(request, 'Draft saved successfully!')
                return redirect('drafts')
            else:
                # If draft form is invalid, create a compose form with the data to show errors
                form = ComposeMailForm(user=request.user, data=request.POST)
        else:
            # For any other action, create a form with the posted data
            form = ComposeMailForm(user=request.user, data=request.POST)
    else:
        form = ComposeMailForm(user=request.user)
    
    # Check if user has projects
    user_projects_count = 0
    if hasattr(request.user, 'userprofile'):
        user_projects_count = request.user.userprofile.projects.count()
    
    if user_projects_count == 0:
        messages.info(request, 'You are not a member of any projects. Please join or create a project first.')
    
    return render(request, 'mailapp/compose.html', {'form': form})

@login_required
def drafts(request):
    user_drafts = Draft.objects.filter(author=request.user).order_by('-updated_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query and search_query.lower() != 'none':
        user_drafts = user_drafts.filter(
            Q(subject__icontains=search_query) |
            Q(body__icontains=search_query) |
            Q(recipient__username__icontains=search_query) |
            Q(recipient__first_name__icontains=search_query) |
            Q(recipient__last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(user_drafts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query if search_query.lower() != 'none' else '',
    }
    
    return render(request, 'mailapp/drafts.html', context)

@login_required
def edit_draft(request, draft_id):
    draft = get_object_or_404(Draft, id=draft_id, author=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'send':
            # Convert draft to mail
            if draft.recipient and draft.project:
                Mail.objects.create(
                    sender=request.user,
                    recipient=draft.recipient,
                    project=draft.project,
                    subject=draft.subject,
                    body=draft.body
                )
                draft.delete()
                messages.success(request, 'Mail sent successfully!')
                return redirect('inbox')
            else:
                messages.error(request, 'Please select both project and recipient before sending.')
        
        elif action == 'update':
            form = DraftForm(user=request.user, data=request.POST, instance=draft)
            if form.is_valid():
                form.save()
                messages.success(request, 'Draft updated successfully!')
                return redirect('drafts')
        
        elif action == 'delete':
            draft.delete()
            messages.success(request, 'Draft deleted successfully!')
            return redirect('drafts')
    
    # Pre-populate form with draft data
    initial_data = {
        'project': draft.project,
        'recipient': draft.recipient,
        'subject': draft.subject,
        'body': draft.body,
    }
    form = DraftForm(user=request.user, initial=initial_data, instance=draft)
    
    # If draft has a project, populate recipients
    if draft.project:
        project_members = User.objects.filter(userprofile__projects=draft.project).exclude(id=request.user.id)
        form.fields['recipient'].queryset = project_members
    
    return render(request, 'mailapp/edit_draft.html', {'form': form, 'draft': draft})

@login_required
def read_mail(request, mail_id):
    # Allow both sender and recipient to view the mail
    mail = get_object_or_404(Mail, id=mail_id)
    
    # Check if user is either sender or recipient
    if mail.sender != request.user and mail.recipient != request.user:
        messages.error(request, 'You do not have permission to view this mail.')
        return redirect('inbox')
    
    # Mark as read only if user is the recipient
    if mail.recipient == request.user and not mail.is_read:
        mail.is_read = True
        mail.save()
    
    return render(request, 'mailapp/read_mail.html', {'mail': mail})

@login_required
def get_project_users(request):
    """AJAX view to get users for a specific project"""
    project_id = request.GET.get('project_id')
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
            # Get users that are members of this project, excluding the current user
            users = User.objects.filter(
                userprofile__projects=project
            ).exclude(id=request.user.id).values('id', 'username', 'first_name', 'last_name')
            
            user_list = []
            for user in users:
                display_name = f"{user['first_name']} {user['last_name']}".strip()
                if display_name:
                    display_name = f"{display_name} ({user['username']})"
                else:
                    display_name = user['username']
                
                user_list.append({
                    'id': user['id'], 
                    'name': display_name
                })
            
            return JsonResponse({'users': user_list})
        except Project.DoesNotExist:
            return JsonResponse({'error': 'Project not found', 'users': []})
        except Exception as e:
            return JsonResponse({'error': str(e), 'users': []})
    
    return JsonResponse({'error': 'No project ID provided', 'users': []})

@login_required
def manage_projects(request):
    """View for users to manage their project memberships"""
    user_profile = request.user.userprofile
    user_projects = user_profile.projects.all()
    available_projects = Project.objects.exclude(members=user_profile)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        project_id = request.POST.get('project_id')
        
        try:
            project = Project.objects.get(id=project_id)
            
            if action == 'join':
                user_profile.projects.add(project)
                messages.success(request, f'Successfully joined project: {project.name}')
            elif action == 'leave':
                user_profile.projects.remove(project)
                messages.success(request, f'Successfully left project: {project.name}')
            
            return redirect('manage_projects')
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
    
    context = {
        'user_projects': user_projects,
        'available_projects': available_projects,
    }
    
    return render(request, 'mailapp/manage_projects.html', context)

@login_required
def create_project(request):
    """View for users to create new projects"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            try:
                project = Project.objects.create(
                    name=name,
                    description=description,
                    created_by=request.user
                )
                # Automatically add the creator to the project
                request.user.userprofile.projects.add(project)
                messages.success(request, f'Project "{name}" created successfully!')
                return redirect('manage_projects')
            except:
                messages.error(request, 'A project with this name already exists.')
        else:
            messages.error(request, 'Project name is required.')
    
    return render(request, 'mailapp/create_project.html')

def home(request):
    if request.user.is_authenticated:
        return redirect('inbox')
    return render(request, 'mailapp/home.html')

@login_required
def debug_project_data(request):
    """Debug view to check user's project data"""
    from django.http import JsonResponse
    
    debug_info = {
        'user_id': request.user.id,
        'username': request.user.username,
        'has_userprofile': hasattr(request.user, 'userprofile'),
        'userprofile_exists': False,
        'user_projects_count': 0,
        'user_projects': [],
        'total_projects_count': Project.objects.count(),
        'all_projects': [],
        'error': None
    }
    
    try:
        # Check if UserProfile exists
        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            debug_info['userprofile_exists'] = True
            debug_info['user_projects_count'] = profile.projects.count()
            debug_info['user_projects'] = [
                {
                    'id': p.id, 
                    'name': p.name, 
                    'description': p.description,
                    'member_count': p.members.count()
                } 
                for p in profile.projects.all()
            ]
        else:
            debug_info['error'] = 'UserProfile does not exist'
            
        # Get all projects
        debug_info['all_projects'] = [
            {
                'id': p.id, 
                'name': p.name, 
                'description': p.description,
                'created_by': p.created_by.username,
                'member_count': p.members.count(),
                'members': [
                    {
                        'id': u.user.id,
                        'username': u.user.username,
                        'name': f"{u.user.first_name} {u.user.last_name}".strip()
                    }
                    for u in p.members.all()
                ]
            } 
            for p in Project.objects.all()
        ]
        
    except Exception as e:
        debug_info['error'] = str(e)
    
    return JsonResponse(debug_info)

@login_required
def generate_ai_draft(request):
    """Generate AI-powered draft content using Gemini API"""
    if request.method == 'POST':
        try:
            # Get prompt from request
            prompt = request.POST.get('prompt', '').strip()
            if not prompt:
                return JsonResponse({'error': 'Please provide a prompt for AI generation.'}, status=400)
            
            # Configure Gemini API
            if hasattr(settings, 'GEMINI_API_KEY') and settings.GEMINI_API_KEY != 'your_gemini_api_key_here':
                genai.configure(api_key=settings.GEMINI_API_KEY)
                
                # Create the model
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Enhanced prompt for email generation
                enhanced_prompt = f"""
                Generate a professional email based on the following request: {prompt}
                
                Please format the response as JSON with the following structure:
                {{
                    "subject": "appropriate email subject",
                    "body": "email body content"
                }}
                
                Guidelines:
                - Keep the tone professional and courteous
                - Make the subject concise and relevant
                - Structure the body with proper greeting, content, and closing
                - Ensure the content is appropriate for a business/project communication
                """
                
                # Generate content
                response = model.generate_content(enhanced_prompt)
                
                # Try to parse JSON response
                import json
                try:
                    # Extract JSON from response text
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '').strip()
                    elif response_text.startswith('```'):
                        response_text = response_text.replace('```', '').strip()
                    
                    ai_content = json.loads(response_text)
                    
                    return JsonResponse({
                        'success': True,
                        'subject': ai_content.get('subject', ''),
                        'body': ai_content.get('body', '')
                    })
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract content manually
                    content = response.text.strip()
                    
                    # Simple extraction - split by common patterns
                    subject = ''
                    body = content
                    
                    # Try to extract subject if present
                    if 'Subject:' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if line.strip().lower().startswith('subject:'):
                                subject = line.split(':', 1)[1].strip()
                                body = content.replace(line, '').strip()
                                break
                    
                    return JsonResponse({
                        'success': True,
                        'subject': subject,
                        'body': body
                    })
                    
            else:
                return JsonResponse({'error': 'Gemini API key not configured. Please add your API key to settings.py'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': f'Error generating AI content: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def debug_user_data(request):
    """Debug view to check user's project data"""
    debug_info = {}
    
    # Check if user has profile
    debug_info['has_userprofile'] = hasattr(request.user, 'userprofile')
    
    if hasattr(request.user, 'userprofile'):
        profile = request.user.userprofile
        user_projects = profile.projects.all()
        debug_info['user_projects_count'] = user_projects.count()
        debug_info['user_projects'] = [{'id': p.id, 'name': p.name} for p in user_projects]
        
        # Check project members for each project
        for project in user_projects:
            members = User.objects.filter(userprofile__projects=project)
            debug_info[f'project_{project.id}_members'] = [
                {'id': u.id, 'username': u.username, 'name': f"{u.first_name} {u.last_name}"}
                for u in members
            ]
    else:
        debug_info['user_projects_count'] = 0
        debug_info['user_projects'] = []
    
    # Check all projects in system
    all_projects = Project.objects.all()
    debug_info['total_projects'] = all_projects.count()
    debug_info['all_projects'] = [{'id': p.id, 'name': p.name, 'created_by': p.created_by.username} for p in all_projects]
    
    return JsonResponse(debug_info)

def health_check(request):
    """Health check endpoint for debugging deployment issues"""
    try:
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test model access
        user_count = User.objects.count()
        profile_count = UserProfile.objects.count()
        project_count = Project.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'users': user_count,
            'profiles': profile_count,
            'projects': project_count,
            'debug': settings.DEBUG,
            'database_url': 'configured' if settings.DATABASES['default']['NAME'] else 'missing'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'type': type(e).__name__
        }, status=500)
