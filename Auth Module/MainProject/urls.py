
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from rest_framework.documentation import include_docs_urls


schema_view = get_swagger_view(title="BookieBot")
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('api.urls')),
    url(r'^$', schema_view),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)