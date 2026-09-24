from datetime import datetime, time, timedelta
import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, Workspace
from lessons.models import Attendance, Lesson, LessonNote, Location
from students.models import Skill, Student, StudentSkill, StudentSkillHistory


class Command(BaseCommand):
    help = 'Yerel prototip için örnek eğitmen, öğrenci ve ders verisi oluşturur.'

    def handle(self, *args, **options):
        demo_email = os.getenv('DEMO_EMAIL', 'kazmshn@gmail.com')
        demo_password = os.getenv('DEMO_PASSWORD')
        if not demo_password:
            self.stdout.write(self.style.ERROR('DEMO_PASSWORD .env içinde tanımlı değil.'))
            return
        workspace, _ = Workspace.objects.get_or_create(name='Paten Akış Demo', defaults={'timezone': 'Europe/Istanbul'})
        instructor, created = User.objects.get_or_create(
            username=demo_email,
            defaults={'email': demo_email, 'first_name': 'Deniz', 'last_name': 'Eğitmen', 'workspace': workspace},
        )
        instructor.username = demo_email
        instructor.email = demo_email
        instructor.workspace = workspace
        instructor.first_name = instructor.first_name or 'Deniz'
        instructor.last_name = instructor.last_name or 'Eğitmen'
        instructor.set_password(demo_password)
        instructor.save()

        park, _ = Location.objects.get_or_create(workspace=workspace, name='Caddebostan Sahil', defaults={'address': 'Kadıköy, İstanbul'})
        salon, _ = Location.objects.get_or_create(workspace=workspace, name='Belediye Spor Salonu', defaults={'address': 'Ataşehir, İstanbul'})
        people = [
            ('Zeynep', 'Yılmaz', 'Başlangıç', 'Denge ve fren üzerinde çalışıyor.'),
            ('Mert', 'Kaya', 'Temel', 'Dönüşlerde güveni artıyor.'),
            ('Ece', 'Demir', 'Orta', 'Geri kayma ve slalom çalışıyor.'),
            ('Arda', 'Şahin', 'İleri', 'Cross-over tekrarları planlanacak.'),
            ('Ada', 'Çelik', 'Başlangıç', 'İlk ders öncesi ekipman kontrolü yapılacak.'),
        ]
        students = []
        for first_name, last_name, level, notes in people:
            student, _ = Student.objects.get_or_create(
                workspace=workspace,
                first_name=first_name,
                last_name=last_name,
                defaults={'level': level, 'notes': notes, 'phone': '05XX XXX XX XX'},
            )
            students.append(student)

        skill_names = ['Denge', 'İleri kayma', 'Fren', 'Dönüş', 'Geri kayma', 'Slalom', 'Cross-over', 'Tek ayak denge']
        skills = []
        for order, name in enumerate(skill_names, start=1):
            skill, _ = Skill.objects.get_or_create(workspace=workspace, name=name, defaults={'sort_order': order})
            skills.append(skill)

        base = timezone.localdate()
        lesson_specs = [
            (-1, time(18, 0), time(19, 0), Lesson.LessonType.ONE_TO_ONE, [students[0]], Lesson.Status.COMPLETED, park),
            (0, time(10, 0), time(11, 0), Lesson.LessonType.GROUP, [students[1], students[2]], Lesson.Status.PLANNED, park),
            (0, time(17, 30), time(18, 30), Lesson.LessonType.ONE_TO_ONE, [students[3]], Lesson.Status.PLANNED, salon),
            (2, time(11, 0), time(12, 0), Lesson.LessonType.GROUP, [students[0], students[4]], Lesson.Status.PLANNED, park),
        ]
        for offset, start_time, end_time, lesson_type, lesson_students, status, location in lesson_specs:
            day = base + timedelta(days=offset)
            starts_at = timezone.make_aware(datetime.combine(day, start_time))
            ends_at = timezone.make_aware(datetime.combine(day, end_time))
            lesson, _ = Lesson.objects.get_or_create(
                workspace=workspace, instructor=instructor, starts_at=starts_at,
                defaults={'ends_at': ends_at, 'lesson_type': lesson_type, 'status': status, 'location': location, 'instructor_note': 'Bir sonraki derste kısa tekrar yapılacak.'},
            )
            for student in lesson_students:
                attendance, _ = Attendance.objects.get_or_create(lesson=lesson, student=student)
                if status == Lesson.Status.COMPLETED:
                    attendance.status = Attendance.Status.ATTENDED
                    attendance.recorded_by = instructor
                    attendance.recorded_at = timezone.now()
                    attendance.save()
            if status == Lesson.Status.COMPLETED:
                LessonNote.objects.get_or_create(
                    workspace=workspace, student=lesson_students[0], lesson=lesson,
                    defaults={'text': 'Denge çalışıldı. Fren kontrolü iyi ilerliyor.', 'noted_on': day, 'author': instructor},
                )

        demo_statuses = [StudentSkill.Status.PRACTICING, StudentSkill.Status.CAN_DO, StudentSkill.Status.GOOD]
        for index, student in enumerate(students[:3]):
            for skill_index, skill in enumerate(skills[:4]):
                status = demo_statuses[(index + skill_index) % len(demo_statuses)]
                assessment, _ = StudentSkill.objects.get_or_create(
                    student=student, skill=skill,
                    defaults={'status': status, 'evaluated_on': base, 'note': 'Demo değerlendirmesi.'},
                )
                StudentSkillHistory.objects.get_or_create(
                    student=student, skill=skill, evaluated_on=base,
                    defaults={'status': assessment.status, 'note': assessment.note, 'created_by': instructor},
                )

        self.stdout.write(self.style.SUCCESS(f'Demo verileri hazır. Giriş: {demo_email}'))
