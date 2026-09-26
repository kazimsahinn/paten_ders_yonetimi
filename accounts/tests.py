from django.contrib.auth.tokens import default_token_generator
import json
import tempfile
from pathlib import Path

from django.core import management
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail

from .models import AuditLog, User, Workspace
from students.models import Student, StudentSafetyProfile
from cryptography.fernet import Fernet


class AuthenticationTests(TestCase):
    def test_login_redirects_to_dashboard(self):
        workspace = Workspace.objects.create(name='Test çalışma alanı')
        User.objects.create_user(
            username='egitmen@example.com', email='egitmen@example.com', password='GuvenliTest123!', workspace=workspace
        )
        response = self.client.post(reverse('login'), {'username': 'egitmen@example.com', 'password': 'GuvenliTest123!'})
        self.assertRedirects(response, reverse('dashboard'))

    def test_anonymous_user_is_redirected_from_student_list(self):
        response = self.client.get(reverse('student_list'))
        self.assertRedirects(response, f'{reverse("login")}?next={reverse("student_list")}')

    def test_mobile_navigation_contains_lessons_and_account_actions(self):
        workspace = Workspace.objects.create(name='Test çalışma alanı')
        user = User.objects.create_user(
            username='mobile@example.com', email='mobile@example.com', password='GuvenliTest123!', workspace=workspace
        )
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'Mobil gezinme')
        self.assertContains(response, reverse('lesson_list'))
        self.assertContains(response, reverse('password_change'))
        self.assertContains(response, reverse('logout'))
        self.assertContains(response, 'Çıkış yap')

    def test_unknown_url_uses_friendly_404_page(self):
        response = self.client.get('/olmayan-sayfa/')

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'Bu sayfayı bulamadık.', status_code=404)
        self.assertNotContains(response, 'Using the URLconf defined in', status_code=404)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_sends_generic_confirmation(self):
        workspace = Workspace.objects.create(name='Test çalışma alanı')
        User.objects.create_user(
            username='reset@example.com', email='reset@example.com', password='GuvenliTest123!', workspace=workspace
        )

        response = self.client.post(reverse('password_reset'), {'email': 'reset@example.com'})

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('parola yenileme', mail.outbox[0].subject.lower())

    def test_password_reset_changes_password_with_valid_token(self):
        workspace = Workspace.objects.create(name='Test çalışma alanı')
        user = User.objects.create_user(
            username='change@example.com', email='change@example.com', password='EskiGuvenli123!', workspace=workspace
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        confirm_url = reverse('password_reset_confirm', args=[uid, token])
        response = self.client.get(confirm_url)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(response.url, {
            'new_password1': 'YeniGuvenli123!', 'new_password2': 'YeniGuvenli123!',
        })

        self.assertRedirects(response, reverse('password_reset_complete'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('YeniGuvenli123!'))

    def test_authenticated_user_can_change_password_and_stays_signed_in(self):
        workspace = Workspace.objects.create(name='Test çalışma alanı')
        user = User.objects.create_user(
            username='change-auth@example.com', email='change-auth@example.com', password='EskiGuvenli123!', workspace=workspace
        )
        self.client.force_login(user)

        response = self.client.post(reverse('password_change'), {
            'old_password': 'EskiGuvenli123!',
            'new_password1': 'YeniGuvenli123!',
            'new_password2': 'YeniGuvenli123!',
        })

        self.assertRedirects(response, reverse('password_change_done'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('YeniGuvenli123!'))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertTrue(AuditLog.objects.filter(actor=user, action='account.password_changed').exists())

    def test_audit_log_stores_event_without_sensitive_payload(self):
        user = User.objects.create_user(username='audit@example.com', email='audit@example.com', password='GuvenliTest123!', workspace=Workspace.objects.create())
        from .audit import record_event

        record_event(actor=user, action='student.updated', metadata={'level_changed': True})

        event = AuditLog.objects.get(actor=user)
        self.assertEqual(event.workspace, user.workspace)
        self.assertEqual(event.action, 'student.updated')
        self.assertEqual(event.metadata, {'level_changed': True})

    @override_settings(FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode())
    def test_workspace_backup_is_scoped_and_validatable(self):
        workspace = Workspace.objects.create(name='Yedek çalışma alanı')
        user = User.objects.create_user(
            username='backup@example.com', email='backup@example.com', password='GuvenliTest123!', workspace=workspace
        )
        student = Student.objects.create(workspace=user.workspace, first_name='Yedek', last_name='Öğrenci')
        profile = StudentSafetyProfile.objects.create(student=student)
        profile.set_values(safety_note='Yalnız şifreli yedekte bulunmalı.')
        profile.save()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / 'backup.json'
            management.call_command('backup_workspace', workspace_id=workspace.pk, output=path)
            payload = json.loads(path.read_text(encoding='utf-8'))
            management.call_command('verify_backup', path)
            backup_text = path.read_text(encoding='utf-8')

        self.assertEqual(payload['format'], 'paten-akis-workspace-backup')
        self.assertGreater(len(payload['records']), 0)
        self.assertNotIn('Yalnız şifreli yedekte bulunmalı.', backup_text)


class BackupRestoreTests(TransactionTestCase):
    reset_sequences = True

    @override_settings(FIELD_ENCRYPTION_KEY=Fernet.generate_key().decode())
    def test_backup_can_restore_into_empty_database(self):
        workspace = Workspace.objects.create(name='Geri yükleme alanı')
        user = User.objects.create_user(
            username='restore@example.com', email='restore@example.com', password='GuvenliTest123!', workspace=workspace
        )
        student = Student.objects.create(workspace=workspace, first_name='Geri', last_name='Yükleme')
        profile = StudentSafetyProfile.objects.create(student=student)
        profile.set_values(safety_note='Geri yükleme testi güvenlik notu.')
        profile.save()
        from accounts.backup import build_backup

        payload = build_backup(workspace)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / 'backup.json'
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
            management.call_command('flush', interactive=False, verbosity=0)
            management.call_command('restore_workspace_backup', path, confirm_empty_database=True)

        restored = StudentSafetyProfile.objects.get(student__first_name='Geri')
        self.assertEqual(restored.form_values()['safety_note'], 'Geri yükleme testi güvenlik notu.')
        self.assertEqual(Workspace.objects.count(), 1)
        self.assertEqual(User.objects.count(), 1)
