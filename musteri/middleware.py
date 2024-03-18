from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # Giriş sayfası ve diğer istisna URL'ler kontrol ediliyor
            login_url = reverse('login')
            if not request.path.startswith(login_url) and not any(request.path.startswith(url) for url in settings.LOGIN_EXEMPT_URLS):
                return redirect(f'{login_url}?next={request.path}')
        response = self.get_response(request)
        return response
