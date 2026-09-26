from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import EmailAuthenticationForm

urlpatterns = [
    path('giris/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=EmailAuthenticationForm), name='login'),
    path(
        'sifremi-unuttum/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.txt',
            subject_template_name='registration/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path('sifremi-unuttum/gonderildi/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('sifre-yenile/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('sifre-yenilendi/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('parola-degistir/', views.AccountPasswordChangeView.as_view(success_url=reverse_lazy('password_change_done')), name='password_change'),
    path('parola-degistirildi/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('cikis/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
]
