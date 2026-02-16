from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class EnsureAPIKeyMiddleware:
    """
    Middleware to ensure that every authenticated user has a YouTube API key set.
    If not, redirects to the API setup page.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths that are allowed without an API key
        self.allowed_paths = [
            reverse('admin:index'),
            '/admin/', # broad admin match
            reverse('login'),
            reverse('logout'),
            reverse('register'),
            reverse('setup_api_key'),
        ]

    def __call__(self, request):
        # 1. Skip checks for static/media files
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # 2. Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # 3. Skip if path is allowed
        # Simple string match for efficiency, handling trailing slashes if needed
        # We also check if the path *starts with* admin to be safe
        if request.path in self.allowed_paths or request.path.startswith('/admin/'):
            return self.get_response(request)

        # 4. Check if user has API Key
        # We assume UserProfile exists because of signals
        try:
            profile = request.user.profile
            if not profile.google_api_key:
                return redirect('setup_api_key')
        except Exception:
            # If profile doesn't exist (edge case), force setup (view will create it)
            return redirect('setup_api_key')

        return self.get_response(request)
