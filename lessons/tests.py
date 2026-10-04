from datetime import datetime, time

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, Workspace
from accounts.models import AuditLog
from students.models import Student

from .models import Attendance, Lesson, LessonNote, Location


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
        self.assertEqual(event.metadata['changes'][0]['student_id'], self.student.id)

    def test_blank_attendance_is_rejected_without_changing_existing_state(self):
        lesson = self.make_lesson(timezone.localdate(), status=Lesson.Status.COMPLETED)
        attendance = Attendance.objects.create(
            lesson=lesson, student=self.student, status=Attendance.Status.ATTENDED,
        )

        response = self.client.post(reverse('attendance_update', args=[lesson.id]), {
            f'status_{attendance.id}': '',
        })

        self.assertRedirects(response, reverse('lesson_detail', args=[lesson.id]))
        attendance.refresh_from_db()
        lesson.refresh_from_db()
        self.assertEqual(attendance.status, Attendance.Status.ATTENDED)
        self.assertEqual(lesson.status, Lesson.Status.COMPLETED)

    def test_repeated_attendance_submission_does_not_duplicate_lesson_note(self):
        lesson = self.make_lesson(timezone.localdate())
        attendance = Attendance.objects.create(lesson=lesson, student=self.student)
        payload = {
            f'status_{attendance.id}': Attendance.Status.ATTENDED,
            f'note_{attendance.id}': 'Fren çalışıldı.',
        }

        self.client.post(reverse('attendance_update', args=[lesson.id]), payload)
        self.client.post(reverse('attendance_update', args=[lesson.id]), payload)

        self.assertEqual(LessonNote.objects.filter(lesson=lesson, student=self.student).count(), 1)

    def test_cancelled_lesson_cannot_be_reactivated_into_overlap(self):
        day = timezone.localdate()
        cancelled = self.make_lesson(day, status=Lesson.Status.CANCELLED)
        attendance = Attendance.objects.create(
            lesson=cancelled, student=self.student, status=Attendance.Status.CANCELLED,
        )
        self.make_lesson(day, status=Lesson.Status.PLANNED)

        response = self.client.post(reverse('attendance_update', args=[cancelled.id]), {
            f'status_{attendance.id}': Attendance.Status.ATTENDED,
            'correction_reason': 'Ders yeniden planlandı.',
        })

        self.assertRedirects(response, reverse('lesson_detail', args=[cancelled.id]))
        cancelled.refresh_from_db()
        attendance.refresh_from_db()
        self.assertEqual(cancelled.status, Lesson.Status.CANCELLED)
        self.assertEqual(attendance.status, Attendance.Status.CANCELLED)

    def test_attendance_correction_requires_reason_and_records_student_change(self):
        lesson = self.make_lesson(timezone.localdate(), status=Lesson.Status.COMPLETED)
        attendance = Attendance.objects.create(
            lesson=lesson, student=self.student, status=Attendance.Status.ATTENDED,
        )
        url = reverse('attendance_update', args=[lesson.id])

        self.client.post(url, {f'status_{attendance.id}': Attendance.Status.ABSENT})
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, Attendance.Status.ATTENDED)

        self.client.post(url, {
            f'status_{attendance.id}': Attendance.Status.ABSENT,
            'correction_reason': 'Yanlış öğrenci işaretlenmişti.',
        })
        attendance.refresh_from_db()
        event = AuditLog.objects.get(action='attendance.updated')
        self.assertEqual(attendance.status, Attendance.Status.ABSENT)
        self.assertEqual(event.metadata['changes'][0], {
            'student_id': self.student.id,
            'from': Attendance.Status.ATTENDED,
            'to': Attendance.Status.ABSENT,
            'note_changed': False,
        })
        self.assertEqual(event.metadata['correction_reason'], 'Yanlış öğrenci işaretlenmişti.')
