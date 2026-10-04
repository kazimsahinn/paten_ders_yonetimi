from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
urlpatterns = [
    path('giris/', views.RateLimitedLoginView.as_view(), name='login'),
    path('sifremi-unuttum/', views.RateLimitedPasswordResetView.as_view(), name='password_reset'),
    path('sifremi-unuttum/gonderildi/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('sifre-yenile/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('sifre-yenilendi/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('parola-degistir/', views.AccountPasswordChangeView.as_view(success_url=reverse_lazy('password_change_done')), name='password_change'),
    path('parola-degistirildi/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('cikis/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
]
