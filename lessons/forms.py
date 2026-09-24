from django import forms
from django.utils import timezone

from .models import Lesson, Location
from students.models import Student


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address']


class LessonForm(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(queryset=Student.objects.none(), label='Öğrenciler', widget=forms.CheckboxSelectMultiple)
    starts_at = forms.DateTimeField(
        label='Başlangıç',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'],
        localize=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
    )
    ends_at = forms.DateTimeField(
        label='Bitiş',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S'],
        localize=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
    )

    class Meta:
        model = Lesson
        fields = ['starts_at', 'ends_at', 'lesson_type', 'location', 'instructor_note']
        widgets = {
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'instructor_note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, workspace=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(workspace=workspace, is_active=True)
        self.fields['students'].queryset = Student.objects.filter(workspace=workspace, is_active=True)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('starts_at') and cleaned.get('ends_at') and cleaned['ends_at'] <= cleaned['starts_at']:
            self.add_error('ends_at', 'Bitiş saati başlangıçtan sonra olmalıdır.')
        if cleaned.get('lesson_type') == Lesson.LessonType.ONE_TO_ONE and cleaned.get('students') and cleaned['students'].count() != 1:
            self.add_error('students', 'Birebir derste tam bir öğrenci seçin.')
        if cleaned.get('lesson_type') == Lesson.LessonType.GROUP and cleaned.get('students') and cleaned['students'].count() < 2:
            self.add_error('students', 'Grup dersinde en az iki öğrenci seçin.')
        return cleaned
