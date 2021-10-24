from rest_framework.routers import SimpleRouter

from . import views

ROUTER = SimpleRouter()
ROUTER.register(r'', views.PostViewSet, basename="posts")
post_urlpatterns = ROUTER.urls
