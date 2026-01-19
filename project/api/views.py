import threading

class EventTrackingAPIView:
    """Базовый класс для API View с сохранением запроса для событий"""
    
    def dispatch(self, request, *args, **kwargs):
        """Сохраняем запрос в thread local storage для сигналов"""
        thread_local = threading.current_thread()
        thread_local._request = request
        
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            if hasattr(thread_local, '_request'):
                delattr(thread_local, '_request')