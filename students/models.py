from django.conf import settings
from django.db import models


class Student(models.Model):
    class Level(models.TextChoices):
        BEGINNER = 'beginner', 'Başlangıç'
        BASIC = 'basic', 'Temel'
        INTERMEDIATE = 'intermediate', 'Orta'
        ADVANCED = 'advanced', 'İleri'

    workspace = models.ForeignKey('accounts.Workspace', on_delete=models.PROTECT, related_name='students')
    first_name = models.CharField('Ad', max_length=80)
    last_name = models.CharField('Soyad', max_length=80)
    phone = models.CharField('Telefon', max_length=32, blank=True)
    email = models.EmailField('E-posta', blank=True)
    level = models.CharField('Seviye', max_length=20, choices=Level.choices, default=Level.BEGINNER)
    notes = models.TextField('Notlar', blank=True)
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']
        indexes = [models.Index(fields=['workspace', 'is_active', 'last_name'])]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def initials(self):
        return (self.first_name[:1] + self.last_name[:1]).upper()
