from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from lessons.models import Attendance, LessonNote
from .forms import StudentForm
from .models import Skill, Student, StudentLevelHistory, StudentSkill, StudentSkillHistory


def scoped(request):
    return Student.objects.filter(workspace=request.user.workspace)


@login_required
def student_list(request):
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', 'active')
    students = scoped(request)
    if query:
        students = students.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(phone__icontains=query))
    if status in {'active', 'inactive'}:
        students = students.filter(is_active=status == 'active')
    return render(request, 'students/list.html', {'students': students, 'query': query, 'status': status})


@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    students = scoped(request).none()
    if query:
        students = scoped(request).filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )
    return render(request, 'students/search.html', {'query': query, 'students': students})


@login_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.workspace = request.user.workspace
        student.save()
        StudentLevelHistory.objects.create(student=student, level=student.level, effective_on=timezone.localdate(), note='İlk öğrenci kaydı.', changed_by=request.user)
        return redirect('student_detail', student_id=student.id)
    return render(request, 'students/form.html', {'form': form, 'title': 'Yeni öğrenci'})


@login_required
def student_update(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    previous_level = student.level
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if previous_level != student.level:
            StudentLevelHistory.objects.create(student=student, level=student.level, effective_on=timezone.localdate(), note='Seviye güncellendi.', changed_by=request.user)
        return redirect('student_detail', student_id=student.id)
    return render(request, 'students/form.html', {'form': form, 'title': 'Öğrenciyi düzenle', 'student': student})


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    attendances = Attendance.objects.filter(student=student).select_related('lesson', 'lesson__location')[:20]
    notes = LessonNote.objects.filter(student=student).select_related('lesson')[:10]
    latest_skills = student.skill_assessments.select_related('skill').filter(skill__is_active=True)
    level_history = student.level_history.select_related('changed_by')[:10]
    return render(request, 'students/detail.html', {'student': student, 'attendances': attendances, 'notes': notes, 'latest_skills': latest_skills, 'level_history': level_history})


@login_required
def student_development(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    skills = list(Skill.objects.filter(workspace=request.user.workspace, is_active=True))
    assessments = {item.skill_id: item for item in student.skill_assessments.select_related('skill')}
    if request.method == 'POST':
        evaluated_on = request.POST.get('evaluated_on') or timezone.localdate().isoformat()
        try:
            evaluated_on = timezone.datetime.strptime(evaluated_on, '%Y-%m-%d').date()
        except ValueError:
            evaluated_on = timezone.localdate()
        with transaction.atomic():
            for skill in skills:
                status = request.POST.get(f'status_{skill.id}', '')
                if status not in dict(StudentSkill.Status.choices) or not status:
                    continue
                note = request.POST.get(f'note_{skill.id}', '').strip()
                current = assessments.get(skill.id)
                if current is None:
                    current = StudentSkill.objects.create(student=student, skill=skill, status=status, evaluated_on=evaluated_on, note=note)
                    changed = True
                else:
                    changed = current.status != status or current.note != note or current.evaluated_on != evaluated_on
                    current.status = status
                    current.evaluated_on = evaluated_on
                    current.note = note
                    current.save()
                if changed:
                    StudentSkillHistory.objects.create(student=student, skill=skill, status=status, evaluated_on=evaluated_on, note=note, created_by=request.user)
        messages.success(request, 'Gelişim değerlendirmeleri kaydedildi.')
        return redirect('student_development', student_id=student.id)
    history = student.skill_history.select_related('skill', 'created_by')[:30]
    skill_rows = [{'skill': skill, 'assessment': assessments.get(skill.id)} for skill in skills]
    return render(request, 'students/development.html', {
        'student': student, 'skill_rows': skill_rows, 'status_choices': StudentSkill.Status.choices,
        'history': history, 'today': timezone.localdate(),
    })


@login_required
def student_delete(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    if request.method == 'POST':
        name = str(student)
        student.delete()
        messages.success(request, f'{name} öğrencisi silindi.')
        return redirect('student_list')
    return redirect('student_detail', student_id=student.id)
