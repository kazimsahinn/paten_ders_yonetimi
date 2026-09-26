from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _fernet():
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        raise ImproperlyConfigured('FIELD_ENCRYPTION_KEY ayarlanmalıdır.')
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured('FIELD_ENCRYPTION_KEY geçerli bir Fernet anahtarı olmalıdır.') from exc


def encrypt_text(value):
    if not value:
        return ''
    return _fernet().encrypt(value.strip().encode('utf-8')).decode('ascii')


def decrypt_text(value):
    if not value:
        return ''
    try:
        return _fernet().decrypt(value.encode('ascii')).decode('utf-8')
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise ImproperlyConfigured('Şifreli öğrenci güvenlik verisi çözülemedi.') from exc
