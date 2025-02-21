from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

# Необхідні маршрути
urlpatterns = [
    path("admin/", admin.site.urls),  # Адмінка Django
    # Можна додати необхідні маршрути для вашого проекту тут
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Відключаємо групи та користувачів з адмінки
admin.site.unregister(Group)
admin.site.unregister(User)
