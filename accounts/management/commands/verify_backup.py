import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from accounts.backup import BACKUP_FORMAT, BACKUP_VERSION


class Command(BaseCommand):
    help = 'Çalışma alanı JSON yedeğinin biçimini ve kayıt model listesini doğrular.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=Path)

    def handle(self, *args, **options):
        path = options['path']
        if not path.is_file():
            raise CommandError('Yedek dosyası bulunamadı.')
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError('Yedek dosyası okunamadı veya JSON biçimi geçersiz.') from exc
        if payload.get('format') != BACKUP_FORMAT or payload.get('version') != BACKUP_VERSION:
            raise CommandError('Yedek biçimi veya sürümü desteklenmiyor.')
        if not isinstance(payload.get('workspace_id'), int) or not isinstance(payload.get('records'), list):
            raise CommandError('Yedek manifesti eksik.')
        for record in payload['records']:
            if not isinstance(record, dict) or not isinstance(record.get('model'), str) or not isinstance(record.get('fields'), dict):
                raise CommandError('Yedekte geçersiz kayıt bulundu.')
        self.stdout.write(self.style.SUCCESS(f'Yedek geçerli: {len(payload["records"])} kayıt, çalışma alanı {payload["workspace_id"]}.'))
