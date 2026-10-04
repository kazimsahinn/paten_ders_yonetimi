import math
import os
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .models import AuthThrottle


def throttle_key(action, value):
    normalized = (value or '').strip().casefold()
    return salted_hmac('accounts.auth-throttle', f'{action}:{normalized}').hexdigest()


def client_address(request):
    if os.getenv('VERCEL') == '1':
        forwarded = request.META.get('HTTP_X_VERCEL_FORWARDED_FOR')
        if forwarded:
            return forwarded.strip()
    return request.META.get('REMOTE_ADDR') or 'unknown'


def consume_attempt(*, action, value, limit, window_seconds, block_seconds):
    """Consume one attempt and return remaining block seconds, or zero."""
    key_hash = throttle_key(action, value)
    for retry in range(2):
        try:
            with transaction.atomic():
                counter = AuthThrottle.objects.select_for_update().filter(
                    action=action, key_hash=key_hash,
                ).first()
                now = timezone.now()
                if counter is None:
                    counter = AuthThrottle.objects.create(
                        action=action, key_hash=key_hash, attempts=0, window_started=now,
                    )
                if counter.blocked_until and counter.blocked_until > now:
                    return max(1, math.ceil((counter.blocked_until - now).total_seconds()))
                if now >= counter.window_started + timedelta(seconds=window_seconds):
                    counter.attempts = 0
                    counter.window_started = now
                    counter.blocked_until = None
                if counter.attempts >= limit:
                    counter.blocked_until = now + timedelta(seconds=block_seconds)
                    counter.save(update_fields=['blocked_until', 'updated_at'])
                    return block_seconds
                counter.attempts += 1
                counter.save(update_fields=['attempts', 'window_started', 'blocked_until', 'updated_at'])
                return 0
        except IntegrityError:
            if retry:
                raise
    return 0


def clear_attempts(*, action, value):
    AuthThrottle.objects.filter(action=action, key_hash=throttle_key(action, value)).delete()
