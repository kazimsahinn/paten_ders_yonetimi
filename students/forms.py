from django import forms

from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'phone', 'email', 'level', 'notes', 'is_active']
        widgets = {'notes': forms.Textarea(attrs={'rows': 4})}


class StudentSafetyProfileForm(forms.Form):
    emergency_contact_name = forms.CharField(label='Acil durumda aranacak kişi', max_length=120, required=False)
    emergency_contact_phone = forms.CharField(label='Acil iletişim telefonu', max_length=32, required=False)
    safety_note = forms.CharField(
        label='Güvenlik notu', max_length=1000, required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Yalnız güvenli ders yürütmek için gerekli kısa bilgiyi yazın.'}),
    )
