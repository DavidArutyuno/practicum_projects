from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year_not_in_future(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(f'Год не может быть больше {current_year}.')
