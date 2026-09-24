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


class Skill(models.Model):
    workspace = models.ForeignKey('accounts.Workspace', on_delete=models.PROTECT, related_name='skills')
    name = models.CharField('Beceri adı', max_length=100)
    sort_order = models.PositiveIntegerField('Sıra', default=0)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        ordering = ['sort_order', 'name']
        constraints = [models.UniqueConstraint(fields=['workspace', 'name'], name='unique_workspace_skill')]

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    class Status(models.TextChoices):
        NOT_ASSESSED = '', 'Değerlendirilmedi'
        NOT_LEARNED = 'not_learned', 'Öğrenilmedi'
        PRACTICING = 'practicing', 'Çalışılıyor'
        CAN_DO = 'can_do', 'Yapabiliyor'
        GOOD = 'good', 'İyi'
        MASTERED = 'mastered', 'Ustalaştı'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='skill_assessments')
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name='student_assessments')
    status = models.CharField('Durum', max_length=20, choices=Status.choices, blank=True, default='')
    evaluated_on = models.DateField('Değerlendirme tarihi', null=True, blank=True)
    note = models.CharField('Kısa açıklama', max_length=240, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['student', 'skill'], name='unique_student_skill')]


class StudentSkillHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='skill_history')
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name='history')
    status = models.CharField('Durum', max_length=20, choices=StudentSkill.Status.choices)
    evaluated_on = models.DateField('Değerlendirme tarihi')
    note = models.CharField('Kısa açıklama', max_length=240, blank=True)
    lesson = models.ForeignKey('lessons.Lesson', null=True, blank=True, on_delete=models.SET_NULL, related_name='skill_history')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-evaluated_on', '-created_at']
