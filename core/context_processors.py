"""
Context processors for templates.
"""
from notifications.models import Notification


def notifications_context(request):
    """
    Add notification-related context to all templates.
    """
    context = {}
    
    if request.user.is_authenticated:
        # Check if user has pending notifications
        context['has_pending_notifications'] = Notification.objects.filter(
            user=request.user,
            status='PENDING'
        ).exists()
    else:
        context['has_pending_notifications'] = False
    
    return context
