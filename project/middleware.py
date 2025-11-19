from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_URLS = [reverse('login'), '/static/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not any(request.path.startswith(url) for url in EXEMPT_URLS):
            return redirect('login')
        return self.get_response(request)