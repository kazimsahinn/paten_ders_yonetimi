from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.utils import timezone

from .audit import record_event
from .forms import EmailAuthenticationForm
from .throttling import clear_attempts, client_address, consume_attempt
from lessons.models import Lesson
from students.models import Student


class AccountPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'registration/password_change_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        record_event(actor=self.request.user, action='account.password_changed')
        return response


class RateLimitedLoginView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = EmailAuthenticationForm

    def post(self, request, *args, **kwargs):
        email = request.POST.get('username', '')
        address = client_address(request)
        limits = (
            ('login_account', email),
            ('login_address', address),
        )
        retry_after = max(
            consume_attempt(
                action=action,
                value=value,
                limit=settings.AUTH_LOGIN_ATTEMPTS,
                window_seconds=settings.AUTH_LOGIN_WINDOW_SECONDS,
                block_seconds=settings.AUTH_LOGIN_BLOCK_SECONDS,
            )
            for action, value in limits
        )
        if retry_after:
            form = self.get_form()
            form.add_error(None, f'Çok fazla giriş denemesi yapıldı. {retry_after} saniye sonra yeniden deneyin.')
            response = self.form_invalid(form)
            response.status_code = 429
            response['Retry-After'] = str(retry_after)
            return response
        response = super().post(request, *args, **kwargs)
        if response.status_code in {301, 302, 303, 307, 308}:
            for action, value in limits:
                clear_attempts(action=action, value=value)
        return response


class RateLimitedPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '')
        address = client_address(request)
        limits = (
            ('password_reset_account', email),
            ('password_reset_address', address),
        )
        retry_after = max(
            consume_attempt(
                action=action,
                value=value,
                limit=settings.AUTH_PASSWORD_RESET_ATTEMPTS,
                window_seconds=settings.AUTH_PASSWORD_RESET_WINDOW_SECONDS,
                block_seconds=settings.AUTH_PASSWORD_RESET_BLOCK_SECONDS,
            )
            for action, value in limits
        )
        if retry_after:
            form = self.get_form()
            form.add_error(None, f'Çok fazla bağlantı isteği yapıldı. {retry_after} saniye sonra yeniden deneyin.')
            response = self.form_invalid(form)
            response.status_code = 429
            response['Retry-After'] = str(retry_after)
            return response
        return super().post(request, *args, **kwargs)


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


@login_required
@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')
