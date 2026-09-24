from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.utils import timezone

from lessons.models import Lesson
from students.models import Student


@login_required
def dashboard(request):
    today = timezone.localdate()
    lessons = Lesson.objects.filter(workspace=request.user.workspace, starts_at__date=today).select_related('location').prefetch_related('attendances__student')
    upcoming = Lesson.objects.filter(workspace=request.user.workspace, starts_at__gt=timezone.now(), status=Lesson.Status.PLANNED).select_related('location')[:5]
    context = {
        'today': today,
        'today_lessons': lessons,
        'upcoming_lessons': upcoming,
        'active_student_count': Student.objects.filter(workspace=request.user.workspace, is_active=True).count(),
        'recent_students': Student.objects.filter(workspace=request.user.workspace).order_by('-created_at')[:5],
    }
    return render(request, 'dashboard/index.html', context)


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    logout(request)
    return redirect('login')
