"""
SPA Middleware: serves React index.html for any route not handled by Django.
This allows the React Router to handle client-side routing while Django
handles /api/*, /admin/*, and static files.
"""
import os
from django.http import HttpResponse
from django.conf import settings


class SPAMiddleware:
    """
    Catch-all middleware that serves the React SPA index.html for any
    request that:
    - Is a GET request
    - Doesn't start with /api/, /admin/, /static/, /media/
    - Would otherwise 404
    """

    BACKEND_PREFIXES = ('/api/', '/admin/', '/static/', '/media/', '/__debug__/')

    def __init__(self, get_response):
        self.get_response = get_response
        self.index_html = None

    def _load_index(self):
        if self.index_html is not None:
            return self.index_html
        index_path = os.path.join(settings.BASE_DIR, 'frontend_dist', 'index.html')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                self.index_html = f.read()
        except FileNotFoundError:
            self.index_html = ''
        return self.index_html

    def __call__(self, request):
        response = self.get_response(request)

        # Only intercept GET 404s for non-backend paths
        if (
            response.status_code == 404
            and request.method == 'GET'
            and not any(request.path.startswith(p) for p in self.BACKEND_PREFIXES)
        ):
            html = self._load_index()
            if html:
                return HttpResponse(html, content_type='text/html', status=200)

        return response
