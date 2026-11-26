# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrendingMediaView, UserMediaViewSet, search_media, media_detail

router = DefaultRouter()
router.register(r'library', UserMediaViewSet, basename='user-media')


router = DefaultRouter()
router.register(r'library', UserMediaViewSet, basename='user-media')

urlpatterns = [
    path('search/', search_media, name='search-media'),
    path('detail/<str:media_type>/<int:tmdb_id>/', media_detail, name='media-detail'),
    path('trending/', TrendingMediaView.as_view(), name='tmdb-trending'),
    path('', include(router.urls)),
]