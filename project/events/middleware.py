import threading

_user = threading.local()

class CurrentUserMiddleware:
    """
    Сохраняет текущего пользователя в глобальную переменную для сигналов.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = getattr(request, 'user', None)
        response = self.get_response(request)
        _user.value = None
        return response

def get_current_user():
    """
    Возвращает текущего пользователя.
    """
    return getattr(_user, 'value', None)