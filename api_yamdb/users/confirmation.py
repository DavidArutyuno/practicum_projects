import secrets
from email.header import Header

from django.conf import settings
from django.core.mail import EmailMessage


def get_confirmation_code(length=32):
    """"
    Генерируем код подтверждения
    в виде URL-безопасной строки заданной длины.
    """
    return secrets.token_urlsafe(length)


def send_confirmation_code(email, confirmation_code):
    """Отправка на email кода подтверждения."""
    subject = Header(settings.SUBJECT_EMAIL, 'utf-8').encode()
    message = f'{settings.MESSAGE_EMAIL}: {confirmation_code}'
    from_email = settings.DEFAULT_FROM_EMAIL,

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=from_email,
        to=[email],
    )
    email.send(fail_silently=True)
