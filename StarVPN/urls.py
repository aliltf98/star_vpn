from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

# ۱. مسیرهای ثابت (بدون پیشوند زبان /fa/ یا /en/)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

# ۲. مسیرهای دو زبانه سایت
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('account.urls')),
    path('', include('services.urls')),
    prefix_default_language=True
)

# ۳. سرویس‌دهی فایل‌های Static و Media در حالت توسعه (خارج از i18n)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)