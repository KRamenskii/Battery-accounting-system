import threading

class SimpleRequestMiddleware:
    """
    Простой middleware для сохранения запроса в thread local.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Сохраняем запрос в thread local
        thread_local = threading.current_thread()
        thread_local._request = request
        
        # Для отладки
        if hasattr(request, 'user') and request.user.is_authenticated:
            print(f"[SimpleMiddleware] Saving request. User: {request.user.username}")
        else:
            print(f"[SimpleMiddleware] Saving request. Anonymous")
        
        try:
            response = self.get_response(request)
            return response
        finally:
            # Очищаем после обработки
            if hasattr(thread_local, '_request'):
                delattr(thread_local, '_request')