from django.utils import timezone


def year(request):
    """Добавляет в контекст переменную greeting с приветствием."""
    return {
        'year': timezone.now().year,
    }
