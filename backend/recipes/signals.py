from django.db.models.signals import post_save
from django.dispatch import receiver

from core.utils import generate_short_hash
from .models import Recipe


@receiver(post_save, sender=Recipe)
def create_short_link(sender, instance, created, **kwargs):
    """
    Создает короткую ссылку для рецепта после сохранения.

    Генерирует уникальный хэш на основе ID рецепта и сохраняет
    в поле short_link для использования в коротких URL.
    """
    if created and not instance.short_link:
        instance.short_link = generate_short_hash(instance.id)
        Recipe.objects.filter(pk=instance.pk).update(
            short_link=instance.short_link
        )
