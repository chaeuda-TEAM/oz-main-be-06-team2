from a_apis.api.api import api

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("chat/", include("a_chat.urls")),
]

# If DEBUG is True, serve static files in development environment.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
