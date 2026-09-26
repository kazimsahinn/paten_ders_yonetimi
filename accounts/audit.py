from .models import AuditLog


def record_event(*, actor=None, workspace=None, action, target=None, metadata=None):
    """Record a minimal audit event without copying sensitive field contents."""
    if workspace is None and actor is not None:
        workspace = actor.workspace
    AuditLog.objects.create(
        workspace=workspace,
        actor=actor,
        action=action,
        object_type=target.__class__.__name__ if target is not None else '',
        object_id=str(target.pk) if target is not None and target.pk else '',
        metadata=metadata or {},
    )
