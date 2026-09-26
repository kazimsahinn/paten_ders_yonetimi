import json

from django.core import serializers
from django.utils import timezone

from lessons.models import Attendance, Lesson, LessonNote, Location
from students.models import Skill, Student, StudentLevelHistory, StudentSafetyProfile, StudentSkill, StudentSkillHistory

from .models import AuditLog, User, Workspace

BACKUP_FORMAT = 'paten-akis-workspace-backup'
BACKUP_VERSION = 1


def workspace_records(workspace):
    querysets = [
        Workspace.objects.filter(pk=workspace.pk),
        User.objects.filter(workspace=workspace),
        Student.objects.filter(workspace=workspace),
        StudentSafetyProfile.objects.filter(student__workspace=workspace),
        Skill.objects.filter(workspace=workspace),
        Location.objects.filter(workspace=workspace),
        Lesson.objects.filter(workspace=workspace),
        Attendance.objects.filter(lesson__workspace=workspace),
        LessonNote.objects.filter(workspace=workspace),
        StudentLevelHistory.objects.filter(student__workspace=workspace),
        StudentSkill.objects.filter(student__workspace=workspace),
        StudentSkillHistory.objects.filter(student__workspace=workspace),
        AuditLog.objects.filter(workspace=workspace),
    ]
    records = []
    for queryset in querysets:
        records.extend(json.loads(serializers.serialize('json', queryset)))
    return records


def build_backup(workspace):
    records = workspace_records(workspace)
    return {
        'format': BACKUP_FORMAT,
        'version': BACKUP_VERSION,
        'created_at': timezone.now().isoformat(),
        'workspace_id': workspace.pk,
        'workspace_name': workspace.name,
        'encrypted_fields': ['students.studentsafetyprofile.*_ciphertext'],
        'records': records,
    }
