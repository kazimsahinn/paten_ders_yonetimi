from django import forms

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'notes', 'is_active']
        widgets = {'notes': forms.Textarea(attrs={'rows': 4})}
