from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import MediaItem, UserMedia
from .serializers import UserMediaSerializer, MediaItemSerializer
from .services import search_tmdb, get_tmdb_details
from .services import TMDB_BASE_URL

@api_view(['GET'])
@permission_classes([AllowAny])
def search_media(request):
    """
    Endpoint para buscar en TMDb API.
    Ejemplo: GET /api/search/?q=Batman&type=movie
    """
    query = request.GET.get('q', '')
    media_type = request.GET.get('type', 'movie')
    
    if not query:
        return Response({'results': []})
        
    results = search_tmdb(query=query, media_type=media_type)
    return Response({'results': results})

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def media_detail(request, media_type, tmdb_id):
    """
    Devuelve detalles completos de TMDb: elenco, director y plataformas de streaming.
    Ejemplo: GET /api/detail/movie/157336/?region=AR
    """
    region = request.GET.get('region', 'AR').upper()
    data = get_tmdb_details(tmdb_id=tmdb_id, media_type=media_type)
    
    if not data:
        return Response({'error': 'No se encontró el título en TMDb'}, status=status.HTTP_404_NOT_FOUND)

    # Extraemos las plataformas disponibles para el país indicado (ej: AR)
    providers_data = data.get('watch/providers', {}).get('results', {}).get(region, {})
    streaming = [p['provider_name'] for p in providers_data.get('flatrate', [])]
    rent = [p['provider_name'] for p in providers_data.get('rent', [])]

    return Response({
        'tmdb_id': data.get('id'),
        'title': data.get('title') or data.get('name'),
        'overview': data.get('overview'),
        'runtime': data.get('runtime') or (data.get('episode_run_time')[0] if data.get('episode_run_time') else None),
        'genres': [g['name'] for g in data.get('genres', [])],
        'vote_average': data.get('vote_average'),
        'platforms': {
            'streaming': streaming, # Suscripción (Netflix, Prime, Max, Disney+)
            'rent': rent            # Alquiler (Apple TV, Google Play)
        }
    })

class UserMediaViewSet(viewsets.ModelViewSet):
    """
    CRUD completo para el backlog personal del usuario autenticado.
    """
    serializer_class = UserMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve su propia biblioteca
        queryset = UserMedia.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
            
        return queryset

    def perform_create(self, serializer):
        # Guarda automáticamente relacionando al usuario actual
        serializer.save(user=self.request.user)

class TrendingMediaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        url = TMDB_BASE_URL
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "es-AR"
        }
        response = requests.get(url, params=params)
        data = response.json()

        results = []
        for item in data.get("results", []):
            media_type = item.get("media_type")
            if media_type not in ["movie", "tv"]:
                continue
            results.append({
                "tmdb_id": item.get("id"),
                "media_type": media_type,
                "title": item.get("title") if media_type == "movie" else item.get("name"),
                "poster_path": item.get("poster_path"),
                "vote_average": item.get("vote_average"),
                "release_date": item.get("release_date") if media_type == "movie" else item.get("first_air_date"),
            })

        return Response(results[:12])