import json
from pathlib import Path

from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.base import DeserializationError
from django.db import transaction

from accounts.backup import BACKUP_FORMAT, BACKUP_VERSION
from accounts.models import AuditLog, User, Workspace
from lessons.models import Attendance, Lesson, LessonNote, Location
from students.crypto import decrypt_text
from students.models import Skill, Student, StudentLevelHistory, StudentSafetyProfile, StudentSkill, StudentSkillHistory


RESTORE_MODELS = (Workspace, User, Student, StudentSafetyProfile, Skill, Location, Lesson, Attendance, LessonNote, StudentLevelHistory, StudentSkill, StudentSkillHistory, AuditLog)


class Command(BaseCommand):
    help = 'Yedeği yalnızca boş bir veritabanına geri yükler ve şifreli alanları doğrular.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=Path)
        parser.add_argument('--confirm-empty-database', action='store_true')

    def handle(self, *args, **options):
        if not options['confirm_empty_database']:
            raise CommandError('Geri yükleme için --confirm-empty-database bayrağı zorunludur.')
        path = options['path']
        if not path.is_file():
            raise CommandError('Yedek dosyası bulunamadı.')
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError('Yedek dosyası okunamadı veya JSON biçimi geçersiz.') from exc
        if payload.get('format') != BACKUP_FORMAT or payload.get('version') != BACKUP_VERSION:
            raise CommandError('Yedek biçimi veya sürümü desteklenmiyor.')
        existing_model = next((model for model in RESTORE_MODELS if model.objects.exists()), None)
        if existing_model is not None:
            raise CommandError(f'Veritabanı boş değil: {existing_model._meta.label}. Geri yükleme durduruldu.')
        try:
            objects = list(serializers.deserialize('json', json.dumps(payload['records'], ensure_ascii=False)))
        except (KeyError, TypeError, json.JSONDecodeError, DeserializationError) as exc:
            raise CommandError('Yedek kayıtları çözümlenemedi.') from exc
        with transaction.atomic():
            for deserialized in objects:
                deserialized.save()
            for profile in StudentSafetyProfile.objects.all():
                decrypt_text(profile.safety_note_ciphertext)
                decrypt_text(profile.emergency_contact_name_ciphertext)
                decrypt_text(profile.emergency_contact_phone_ciphertext)
        self.stdout.write(self.style.SUCCESS(f'{len(objects)} kayıt geri yüklendi ve şifreli alanlar doğrulandı.'))
