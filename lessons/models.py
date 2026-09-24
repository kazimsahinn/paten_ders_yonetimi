from django.conf import settings
from django.db import models


class Location(models.Model):
    workspace = models.ForeignKey('accounts.Workspace', on_delete=models.PROTECT, related_name='locations')
    name = models.CharField('Lokasyon adı', max_length=120)
    address = models.CharField('Adres', max_length=240, blank=True)
    is_active = models.BooleanField('Aktif', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Lesson(models.Model):
    class LessonType(models.TextChoices):
        ONE_TO_ONE = 'one_to_one', 'Birebir ders'
        GROUP = 'group', 'Grup dersi'

    class Status(models.TextChoices):
        PLANNED = 'planned', 'Planlandı'
        COMPLETED = 'completed', 'Tamamlandı'
        NO_SHOW = 'no_show', 'Öğrenci gelmedi'
        CANCELLED = 'cancelled', 'İptal edildi'

    workspace = models.ForeignKey('accounts.Workspace', on_delete=models.PROTECT, related_name='lessons')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='lessons')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name='lessons')
    starts_at = models.DateTimeField('Başlangıç')
    ends_at = models.DateTimeField('Bitiş')
    lesson_type = models.CharField('Ders türü', max_length=20, choices=LessonType.choices)
    status = models.CharField('Durum', max_length=20, choices=Status.choices, default=Status.PLANNED)
    instructor_note = models.TextField('Eğitmen notu', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['starts_at']
        indexes = [models.Index(fields=['workspace', 'starts_at'])]

    def __str__(self):
        return f'{self.get_lesson_type_display()} · {self.starts_at:%d.%m.%Y %H:%M}'


class Attendance(models.Model):
    class Status(models.TextChoices):
        ATTENDED = 'attended', 'Katıldı'
        ABSENT = 'absent', 'Gelmedi'
        EXCUSED = 'excused', 'İzinli'
        CANCELLED = 'cancelled', 'Ders iptal'

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey('students.Student', on_delete=models.PROTECT, related_name='attendances')
    status = models.CharField('Katılım', max_length=20, choices=Status.choices, blank=True)
    note = models.TextField('Ders notu', blank=True)
    recorded_at = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['lesson', 'student'], name='unique_lesson_student')]


class LessonNote(models.Model):
    workspace = models.ForeignKey('accounts.Workspace', on_delete=models.PROTECT, related_name='lesson_notes')
    student = models.ForeignKey('students.Student', on_delete=models.PROTECT, related_name='lesson_notes')
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL, related_name='notes')
    text = models.TextField('Not')
    noted_on = models.DateField('Not tarihi')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-noted_on', '-created_at']
