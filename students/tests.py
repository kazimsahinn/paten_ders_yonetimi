from datetime import date

from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from accounts.models import AuditLog, User, Workspace
from lessons.models import Attendance, Lesson, Location

from cryptography.fernet import Fernet

from .models import Skill, Student, StudentLevelHistory, StudentSafetyProfile, StudentSkillHistory


class StudentFeatureTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name='Test çalışma alanı')
        self.other_workspace = Workspace.objects.create(name='Diğer çalışma alanı')
        self.user = User.objects.create_user(
            username='egitmen', email='egitmen@example.com', password='GuvenliTest123!', workspace=self.workspace
        )
        self.client.force_login(self.user)
        self.student = Student.objects.create(workspace=self.workspace, first_name='Ayşe', last_name='Kaya', phone='05550000000')
        Student.objects.create(workspace=self.other_workspace, first_name='Mehmet', last_name='Yılmaz')

    def test_global_search_is_limited_to_current_workspace(self):
        response = self.client.get(reverse('global_search'), {'q': 'Mehmet'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['students'].count(), 0)
        response = self.client.get(reverse('global_search'), {'q': 'Ayşe'})
        self.assertContains(response, 'Ayşe')

    def test_student_level_change_creates_history(self):
        response = self.client.post(reverse('student_update', args=[self.student.id]), {
            'first_name': 'Ayşe', 'last_name': 'Kaya', 'phone': '', 'email': '',
            'level': Student.Level.INTERMEDIATE, 'notes': '', 'is_active': 'on',
        })
        self.assertRedirects(response, reverse('student_detail', args=[self.student.id]))
        history = StudentLevelHistory.objects.get(student=self.student)
        self.assertEqual(history.level, Student.Level.INTERMEDIATE)
        self.assertEqual(history.changed_by, self.user)

    def test_student_create_records_audit_event(self):
        response = self.client.post(reverse('student_create'), {
            'first_name': 'Zeynep', 'last_name': 'Demir', 'phone': '', 'email': '',
            'level': Student.Level.BEGINNER, 'notes': '', 'is_active': 'on',
        })
        self.assertEqual(response.status_code, 302)
        event = AuditLog.objects.get(action='student.created')
        self.assertEqual(event.actor, self.user)
        self.assertEqual(event.object_type, 'Student')

    def test_student_export_is_workspace_scoped_and_audited(self):
        response = self.client.get(reverse('student_export', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('Ayşe', response.json()['student']['first_name'])
        self.assertEqual(AuditLog.objects.get(action='student.exported').actor, self.user)

    def test_student_delete_archives_without_removing_record(self):
        response = self.client.post(reverse('student_delete', args=[self.student.id]))
        self.assertRedirects(response, reverse('student_list'))
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_active)
        self.assertTrue(AuditLog.objects.filter(action='student.archived', object_id=str(self.student.id)).exists())

    @override_settings(FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode())
    def test_safety_profile_is_encrypted_and_audited(self):
        response = self.client.post(reverse('student_safety', args=[self.student.id]), {
            'emergency_contact_name': 'Gizli Kişi',
            'emergency_contact_phone': '05551112233',
            'safety_note': 'Ders sırasında bilek desteği kullanılmalı.',
        })
        self.assertRedirects(response, reverse('student_safety', args=[self.student.id]))
        profile = StudentSafetyProfile.objects.get(student=self.student)
        self.assertNotIn('Gizli Kişi', profile.emergency_contact_name_ciphertext)
        self.assertNotIn('bilek desteği', profile.safety_note_ciphertext)
        self.assertEqual(profile.form_values()['safety_note'], 'Ders sırasında bilek desteği kullanılmalı.')
        self.assertTrue(AuditLog.objects.filter(action='student.safety.updated', object_id=str(self.student.id)).exists())

    @override_settings(FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode())
    def test_safety_profile_is_not_in_general_export(self):
        profile = StudentSafetyProfile.objects.create(student=self.student)
        profile.set_values(safety_note='Özel bilgi')
        profile.save()
        response = self.client.get(reverse('student_export', args=[self.student.id]))
        self.assertNotIn('Özel bilgi', response.content.decode())

    def test_development_update_writes_current_and_history(self):
        skill = Skill.objects.create(workspace=self.workspace, name='Fren')
        response = self.client.post(reverse('student_development', args=[self.student.id]), {
            'evaluated_on': '2026-09-26', f'status_{skill.id}': 'practicing',
            f'note_{skill.id}': 'Düz çizgide çalışıldı.',
        })
        self.assertRedirects(response, reverse('student_development', args=[self.student.id]))
        self.assertEqual(self.student.skill_assessments.get(skill=skill).status, 'practicing')
        history = StudentSkillHistory.objects.get(student=self.student, skill=skill)
        self.assertEqual(history.evaluated_on, date(2026, 9, 26))
        self.assertEqual(history.created_by, self.user)
