"""istok URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = i18n_patterns(
    url(r'^api/admin/', admin.site.urls),
    url(r'^api/users/', include('users.urls')),
    url(r'^api/main/', include('main.urls')),
    url(r'^api/blogs/', include('blog.urls')),
    url(r'^api/profiles/', include('profiles.urls')),
    url(r'^api/payments/', include('payments.urls')),
    url(r'^api/tests/', include('tests.urls')),
    prefix_default_language=False
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
    static(settings.ADDITIONAL_URL, document_root=settings.ADDITIONAL_ROOT) + \
    staticfiles_urlpatterns()

admin.site.index_title = ''
admin.site.site_header = 'Панель администрирования ISTOK HOME'
admin.site.site_title = ''
