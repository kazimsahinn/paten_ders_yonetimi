from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Workspace(models.Model):
    name = models.CharField(max_length=120, default='Paten Eğitmeni')
    timezone = models.CharField(max_length=64, default='Europe/Istanbul')
    locale = models.CharField(max_length=16, default='tr-tr')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    workspace = models.ForeignKey(Workspace, null=True, blank=True, on_delete=models.PROTECT, related_name='users')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.get_full_name() or self.email or self.username


class AuditLog(models.Model):
    workspace = models.ForeignKey(Workspace, null=True, blank=True, on_delete=models.PROTECT, related_name='audit_logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='audit_events')
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=80, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['workspace', 'created_at'])]
