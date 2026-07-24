from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification
from accounts.views import role_required

@login_required
def notification_list(request):
    notifications = Notification.objects.select_related('author').all().order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
@role_required(['ADMIN', 'EXAM_CONTROLLER', 'TEACHER'])
def notification_add(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        try:
            Notification.objects.create(
                title=title,
                message=message,
                author=request.user
            )
            messages.success(request, f"Notice '{title}' published successfully.")
        except Exception as e:
            messages.error(request, f"Error publishing notice: {str(e)}")
            
    return redirect('notification_list')
