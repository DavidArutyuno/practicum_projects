from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель, добавляет дату создания."""

    created = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True
