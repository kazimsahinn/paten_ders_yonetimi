from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EmailAuthenticationForm

urlpatterns = [
    path('giris/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=EmailAuthenticationForm), name='login'),
    path('cikis/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
]
