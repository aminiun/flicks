from rest_framework.routers import SimpleRouter

from . import views

ROUTER = SimpleRouter()
ROUTER.register(r'watchlist', views.WatchListViewSet, basename="watchlist")
ROUTER.register(r'watched', views.WatchedViewSet, basename="watched")
ROUTER.register(r'fav', views.FavViewSet, basename="fav")
ROUTER.register(r'search', views.SearchViewSet, basename="search")
ROUTER.register(r'', views.FilmViewSet, basename="film")
film_urlpatterns = ROUTER.urls
