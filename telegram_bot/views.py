from django.http import JsonResponse


def bot_webhook(request):
    """
    Webhook для Telegram бота (будет реализован позже)
    """
    return JsonResponse({'status': 'ok'})