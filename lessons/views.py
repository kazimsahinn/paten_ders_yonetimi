from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from students.models import Student
from .forms import LessonForm, LocationForm
from .models import Attendance, Lesson, LessonNote, Location


def scoped(request):
    return Lesson.objects.filter(workspace=request.user.workspace)


@login_required
def lesson_list(request):
    selected_date = request.GET.get('date') or timezone.localdate().isoformat()
    lessons = scoped(request).filter(starts_at__date=selected_date).select_related('location').prefetch_related('attendances__student')
    return render(request, 'lessons/list.html', {'lessons': lessons, 'selected_date': selected_date})


@login_required
def lesson_create(request):
    form = LessonForm(request.POST or None, workspace=request.user.workspace)
    location_form = LocationForm(request.POST or None, prefix='location')
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            lesson = form.save(commit=False)
            lesson.workspace = request.user.workspace
            lesson.instructor = request.user
            overlap = scoped(request).filter(starts_at__lt=lesson.ends_at, ends_at__gt=lesson.starts_at).exclude(status=Lesson.Status.CANCELLED).exists()
            if overlap:
                form.add_error(None, 'Bu saat aralığında başka bir ders bulunuyor.')
            else:
                lesson.save()
                for student in form.cleaned_data['students']:
                    Attendance.objects.create(lesson=lesson, student=student)
                return redirect('lesson_detail', lesson_id=lesson.id)
    return render(request, 'lessons/form.html', {'form': form, 'location_form': location_form, 'title': 'Yeni ders'})


@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(scoped(request), pk=lesson_id)
    attendances = lesson.attendances.select_related('student')
    return render(request, 'lessons/detail.html', {
        'lesson': lesson,
        'attendances': attendances,
        'attendance_choices': Attendance.Status.choices,
    })


@login_required
def attendance_update(request, lesson_id):
    lesson = get_object_or_404(scoped(request), pk=lesson_id)
    if request.method == 'POST':
        with transaction.atomic():
            rows = list(lesson.attendances.select_for_update().select_related('student'))
            attended = 0
            absent = 0
            for row in rows:
                status = request.POST.get(f'status_{row.id}', '')
                if status in dict(Attendance.Status.choices):
                    row.status = status
                    row.recorded_at = timezone.now()
                    row.recorded_by = request.user
                    row.save(update_fields=['status', 'recorded_at', 'recorded_by'])
                    attended += status == Attendance.Status.ATTENDED
                    absent += status == Attendance.Status.ABSENT
                note = request.POST.get(f'note_{row.id}', '').strip()
                if note:
                    LessonNote.objects.create(workspace=request.user.workspace, student=row.student, lesson=lesson, text=note, noted_on=timezone.localdate(), author=request.user)
            lesson.status = Lesson.Status.COMPLETED if attended else (Lesson.Status.NO_SHOW if absent else Lesson.Status.PLANNED)
            if all(row.status == Attendance.Status.CANCELLED for row in rows):
                lesson.status = Lesson.Status.CANCELLED
            lesson.save(update_fields=['status', 'updated_at'])
        return redirect('lesson_detail', lesson_id=lesson.id)
    return redirect('lesson_detail', lesson_id=lesson.id)
