import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from accounts.backup import build_backup
from accounts.models import Workspace


class Command(BaseCommand):
    help = 'Seçilen çalışma alanının geri yükleme öncesi JSON yedeğini oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument('--workspace-id', type=int, required=True)
        parser.add_argument('--output', type=Path, required=True)
        parser.add_argument('--overwrite', action='store_true')

    def handle(self, *args, **options):
        workspace = Workspace.objects.filter(pk=options['workspace_id']).first()
        if workspace is None:
            raise CommandError('Çalışma alanı bulunamadı.')
        output = options['output']
        if output.exists() and not options['overwrite']:
            raise CommandError('Yedek dosyası zaten var. Üzerine yazmak için --overwrite kullanın.')
        output.parent.mkdir(parents=True, exist_ok=True)
        backup = build_backup(workspace)
        output.write_text(json.dumps(backup, ensure_ascii=False, indent=2), encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'{len(backup["records"])} kayıt yedeklendi: {output}'))
