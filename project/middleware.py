from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            return self.get_response(request)

        try:
            login_url = reverse('login')
        except NoReverseMatch:
            login_url = '/auth/login/'

        # Сюда добавляем все пути, которые не требуют авторизации
        EXEMPT_URLS = [
            login_url,
            '/auth/login/',
            '/auth/logout/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/',
            '/auth/reset/done/',
            '/static/',
            '/admin/',
        ]

        # Пропускаем запрос, если пользователь аутентифицирован или путь в EXEMPT_URLS
        if request.user.is_authenticated or any(request.path.startswith(path) for path in EXEMPT_URLS):
            return self.get_response(request)

        # Иначе редирект на страницу логина
        return redirect(login_url)