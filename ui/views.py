"""
Views for UI app - frontend pages.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from cases.models import MissingPerson
from notifications.models import Notification
from accounts.models import User


def index_view(request):
    """Public dashboard showing all active cases."""
    cases = MissingPerson.objects.filter(status='ACTIVE').order_by('-created_at')[:20]
    return render(request, 'ui/index.html', {'cases': cases})


@login_required
def dashboard_view(request):
    """User dashboard showing their cases."""
    cases = MissingPerson.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'ui/dashboard.html', {'cases': cases})


@login_required
def case_detail_view(request, case_id):
    """Case detail page."""
    try:
        case = MissingPerson.objects.get(id=case_id)
        # Check permission
        if case.reporter != request.user:
            return redirect('ui:dashboard')
        notifications = Notification.objects.filter(missing_person=case).order_by('-created_at')
        return render(request, 'ui/case_detail.html', {
            'case': case,
            'notifications': notifications
        })
    except MissingPerson.DoesNotExist:
        return redirect('ui:dashboard')


@login_required
def notifications_view(request):
    """Notifications page."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'ui/notifications.html', {'notifications': notifications})


def sign_up_view(request):
    """Sign up page."""
    if request.user.is_authenticated:
        return redirect('ui:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone_number = request.POST.get('phone_number', '')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'ui/signup.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number
            )
            # Create token
            token, created = Token.objects.get_or_create(user=user)
            # Login user
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('ui:dashboard')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'ui/signup.html')


def sign_in_view(request):
    """Sign in page."""
    if request.user.is_authenticated:
        return redirect('ui:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('ui:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'ui/signin.html')


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('ui:index')
