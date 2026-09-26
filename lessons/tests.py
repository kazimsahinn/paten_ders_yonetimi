from datetime import datetime, time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, Workspace
from accounts.models import AuditLog
from students.models import Student

from .models import Attendance, Lesson, Location


class LessonFeatureTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name='Test çalışma alanı')
        self.user = User.objects.create_user(
            username='egitmen', email='egitmen@example.com', password='GuvenliTest123!', workspace=self.workspace
        )
        self.client.force_login(self.user)
        self.location = Location.objects.create(workspace=self.workspace, name='Test pist')
        self.student = Student.objects.create(workspace=self.workspace, first_name='Ayşe', last_name='Kaya')

    def make_lesson(self, day, start_hour=10, status=Lesson.Status.PLANNED):
        starts_at = timezone.make_aware(datetime.combine(day, time(start_hour, 0)))
        return Lesson.objects.create(
            workspace=self.workspace, instructor=self.user, location=self.location,
            starts_at=starts_at, ends_at=starts_at + timezone.timedelta(hours=1),
            lesson_type=Lesson.LessonType.ONE_TO_ONE, status=status,
        )

    def test_calendar_month_contains_lesson(self):
        lesson = self.make_lesson(timezone.localdate().replace(day=15))
        response = self.client.get(reverse('calendar'), {'view': 'month', 'date': lesson.starts_at.date().isoformat()})
        self.assertEqual(response.status_code, 200)
        matching_days = [day for day in response.context['days'] if lesson in day['lessons']]
        self.assertEqual(len(matching_days), 1)

    def test_reports_count_selected_month_lessons_and_status(self):
        lesson = self.make_lesson(timezone.localdate().replace(day=10), status=Lesson.Status.COMPLETED)
        Attendance.objects.create(lesson=lesson, student=self.student, status=Attendance.Status.ATTENDED)
        response = self.client.get(reverse('reports'), {'month': lesson.starts_at.strftime('%Y-%m')})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['lesson_count'], 1)
        self.assertEqual(response.context['status_counts'][Lesson.Status.COMPLETED], 1)
        self.assertEqual(list(response.context['top_students']), [self.student])

    def test_lesson_detail_is_workspace_scoped(self):
        foreign_workspace = Workspace.objects.create(name='Diğer çalışma alanı')
        foreign_user = User.objects.create_user(username='diger', email='diger@example.com', password='GuvenliTest123!', workspace=foreign_workspace)
        foreign_location = Location.objects.create(workspace=foreign_workspace, name='Diğer pist')
        starts_at = timezone.make_aware(datetime.combine(timezone.localdate(), time(14, 0)))
        lesson = Lesson.objects.create(
            workspace=foreign_workspace, instructor=foreign_user, location=foreign_location,
            starts_at=starts_at, ends_at=starts_at + timezone.timedelta(hours=1), lesson_type=Lesson.LessonType.ONE_TO_ONE,
        )
        response = self.client.get(reverse('lesson_detail', args=[lesson.id]))
        self.assertEqual(response.status_code, 404)

    def test_attendance_update_records_audit_event(self):
        lesson = self.make_lesson(timezone.localdate())
        attendance = Attendance.objects.create(lesson=lesson, student=self.student)

        response = self.client.post(reverse('attendance_update', args=[lesson.id]), {
            f'status_{attendance.id}': Attendance.Status.ATTENDED,
        })

        self.assertEqual(response.status_code, 302)
        event = AuditLog.objects.get(action='attendance.updated')
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.object_id, str(lesson.id))
        self.assertEqual(event.metadata['attended'], 1)
