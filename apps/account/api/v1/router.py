from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

ROUTER = SimpleRouter()
ROUTER.register(r'', views.FollowViewSet, basename="follow")
ROUTER.register(r'profile', views.SelfProfileViewSet, basename="self_profile")
ROUTER.register(r'search', views.SearchViewSet, basename="search")
ROUTER.register(r'(?P<user_id>\d+)/profile', views.OtherProfileViewSet, basename="other_profile")
ROUTER.register(r'auth', views.AuthViewSet, basename="auth")

account_urlpatterns = ROUTER.urls

account_urlpatterns += [
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
