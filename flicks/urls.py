from django.conf import settings
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

v1_prefix = 'api/v1/'

urlpatterns = [
    path(f'{v1_prefix}account/', include('apps.account.urls')),
    path(f'{v1_prefix}post/', include('apps.post.urls')),
    path(f'{v1_prefix}film/', include('apps.film.urls')),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title=f"{settings.PROJECT_NAME} API",
            default_version='v1',
            contact=openapi.Contact(email="a.aminian321@gmail.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    ]
