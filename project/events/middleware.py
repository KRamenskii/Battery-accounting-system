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
    Минимальная версия с отладкой.
    """
    thread_local = threading.current_thread()
    
    # Проверяем, есть ли сохраненный запрос
    has_request = hasattr(thread_local, '_request')
    print(f"[get_current_user] Has request in thread local: {has_request}")
    
    if not has_request:
        print("[get_current_user] No request saved, returning None")
        return None
    
    request = thread_local._request
    
    # Отладочная информация
    print(f"[get_current_user] Request path: {request.path}")
    print(f"[get_current_user] Request.user exists: {hasattr(request, 'user')}")
    
    if hasattr(request, 'user'):
        print(f"[get_current_user] Request.user: {request.user}")
        print(f"[get_current_user] Request.user.is_authenticated: {request.user.is_authenticated}")
    
    # 1. Для обычных Django views и админки
    if hasattr(request, 'user') and request.user.is_authenticated:
        print(f"[get_current_user] Returning user from request.user: {request.user.username}")
        return request.user
    
    # 2. Для DRF API с токеном
    if hasattr(request, 'auth') and request.auth:
        print(f"[get_current_user] Checking request.auth: {request.auth}")
        if hasattr(request.auth, 'user'):
            print(f"[get_current_user] Returning user from auth.user: {request.auth.user.username}")
            return request.auth.user
        elif hasattr(request.auth, 'user_id'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=request.auth.user_id)
                print(f"[get_current_user] Returning user by user_id: {user.username}")
                return user
            except User.DoesNotExist:
                print(f"[get_current_user] User not found by ID: {request.auth.user_id}")
                pass
    
    print("[get_current_user] No user found, returning None")
    return None