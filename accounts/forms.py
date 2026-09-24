from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='E-posta', widget=forms.EmailInput(attrs={'autocomplete': 'email', 'placeholder': 'ornek@mail.com'}))
    password = forms.CharField(label='Parola', strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'placeholder': '••••••••'}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
