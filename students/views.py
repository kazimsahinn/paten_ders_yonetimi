from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from lessons.models import Attendance, LessonNote
from .forms import StudentForm
from .models import Student


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
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.workspace = request.user.workspace
        student.save()
        return redirect('student_detail', student_id=student.id)
    return render(request, 'students/form.html', {'form': form, 'title': 'Yeni öğrenci'})


@login_required
def student_update(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('student_detail', student_id=student.id)
    return render(request, 'students/form.html', {'form': form, 'title': 'Öğrenciyi düzenle', 'student': student})


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    attendances = Attendance.objects.filter(student=student).select_related('lesson', 'lesson__location')[:20]
    notes = LessonNote.objects.filter(student=student).select_related('lesson')[:10]
    return render(request, 'students/detail.html', {'student': student, 'attendances': attendances, 'notes': notes})


@login_required
def student_delete(request, student_id):
    student = get_object_or_404(scoped(request), pk=student_id)
    if request.method == 'POST':
        name = str(student)
        student.delete()
        messages.success(request, f'{name} öğrencisi silindi.')
        return redirect('student_list')
    return redirect('student_detail', student_id=student.id)
