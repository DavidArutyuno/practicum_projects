import secrets

from django.conf import settings
from django.core.mail import send_mail


def get_confirmation_code(length=32):
    """"
    Генерируем код подтверждения
    в виде URL-безопасной строки заданной длины.
    """
    confirmation_code = secrets.token_urlsafe(length)
    return confirmation_code


def send_confirmation_code(email, confirmation_code):
    """"Отправка на email кода подтверждения."""
    send_mail(
        subject=settings.SUBJECT_EMAIL,
        message=f'{settings.MESSAGE_EMAIL}: {confirmation_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
