import calendar as calendar_module
from datetime import date, datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from students.models import Student
from .forms import LessonForm, LocationForm
from .models import Attendance, Lesson, LessonNote, Location

MONTH_NAMES = ['', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
DAY_NAMES = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']


def scoped(request):
    return Lesson.objects.filter(workspace=request.user.workspace)


@login_required
def lesson_list(request):
    selected_date = request.GET.get('date') or timezone.localdate().isoformat()
    lessons = scoped(request).filter(starts_at__date=selected_date).select_related('location').prefetch_related('attendances__student')
    return render(request, 'lessons/list.html', {'lessons': lessons, 'selected_date': selected_date})


@login_required
def calendar_view(request):
    mode = request.GET.get('view', 'month')
    if mode not in {'day', 'week', 'month'}:
        mode = 'month'
    try:
        anchor = date.fromisoformat(request.GET.get('date', ''))
    except ValueError:
        anchor = timezone.localdate()

    if mode == 'day':
        start = end = anchor
        prev_date = anchor - timedelta(days=1)
        next_date = anchor + timedelta(days=1)
    elif mode == 'week':
        start = anchor - timedelta(days=anchor.weekday())
        end = start + timedelta(days=6)
        prev_date = start - timedelta(days=7)
        next_date = start + timedelta(days=7)
    else:
        start = anchor.replace(day=1)
        end = anchor.replace(day=calendar_module.monthrange(anchor.year, anchor.month)[1])
        prev_month = (start - timedelta(days=1)).replace(day=1)
        next_month = (end + timedelta(days=1)).replace(day=1)
        prev_date = prev_month
        next_date = next_month

    lessons = list(scoped(request).filter(starts_at__date__gte=start, starts_at__date__lte=end).select_related('location').prefetch_related('attendances__student'))
    lessons_by_date = {}
    for lesson in lessons:
        lessons_by_date.setdefault(timezone.localtime(lesson.starts_at).date(), []).append(lesson)

    days = []
    cursor = start
    while cursor <= end:
        days.append({'date': cursor, 'lessons': lessons_by_date.get(cursor, [])})
        cursor += timedelta(days=1)

    month_weeks = []
    if mode == 'month':
        grid_start = start - timedelta(days=start.weekday())
        grid_end = end + timedelta(days=6 - end.weekday())
        cursor = grid_start
        while cursor <= grid_end:
            week = []
            for _ in range(7):
                week.append({'date': cursor, 'in_month': cursor.month == anchor.month, 'lessons': lessons_by_date.get(cursor, [])})
                cursor += timedelta(days=1)
            month_weeks.append(week)

    context = {
        'mode': mode, 'anchor': anchor, 'start': start, 'end': end,
        'prev_date': prev_date, 'next_date': next_date, 'days': days,
        'month_weeks': month_weeks, 'day_names': DAY_NAMES,
        'month_title': f'{MONTH_NAMES[anchor.month]} {anchor.year}',
        'today': timezone.localdate(),
    }
    return render(request, 'lessons/calendar.html', context)


@login_required
def reports_view(request):
    today = timezone.localdate()
    selected_month = request.GET.get('month', today.strftime('%Y-%m'))
    try:
        month_start = datetime.strptime(selected_month, '%Y-%m').date().replace(day=1)
    except ValueError:
        selected_month = today.strftime('%Y-%m')
        month_start = today.replace(day=1)
    next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_end = next_month - timedelta(days=1)
    previous_month = (month_start - timedelta(days=1)).replace(day=1)
    lessons = scoped(request).filter(starts_at__date__gte=month_start, starts_at__date__lte=month_end)
    status_counts = {key: lessons.filter(status=key).count() for key, _ in Lesson.Status.choices}
    status_rows = [{'value': key, 'label': label, 'count': status_counts[key]} for key, label in Lesson.Status.choices]
    top_students = Student.objects.filter(workspace=request.user.workspace).annotate(
        lesson_count=Count('attendances__lesson', filter=Q(attendances__lesson__workspace=request.user.workspace, attendances__lesson__starts_at__date__gte=month_start, attendances__lesson__starts_at__date__lte=month_end), distinct=True)
    ).filter(lesson_count__gt=0).order_by('-lesson_count', 'first_name', 'last_name')[:5]
    context = {
        'month_start': month_start, 'month_end': month_end, 'selected_month': selected_month,
        'previous_month': previous_month, 'next_month': next_month,
        'lesson_count': lessons.count(), 'active_student_count': Student.objects.filter(workspace=request.user.workspace, is_active=True).count(),
        'new_student_count': Student.objects.filter(workspace=request.user.workspace, created_at__date__gte=month_start, created_at__date__lte=month_end).count(),
        'status_counts': status_counts, 'status_rows': status_rows, 'top_students': top_students,
    }
    return render(request, 'lessons/reports.html', context)


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
