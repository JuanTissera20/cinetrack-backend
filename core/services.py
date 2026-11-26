# core/services.py
import requests
from django.conf import settings

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def search_tmdb(query, media_type="movie", language="es-ES"):
    """
    Busca películas o series en TMDb.
    media_type: 'movie' o 'tv'
    """
    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': language,
        'page': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []


def get_tmdb_details(tmdb_id, media_type="movie", language="es-ES"):
    """
    Obtiene los detalles completos de un título, incluyendo proveedores de streaming (JustWatch).
    """
    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': language,
        'append_to_response': 'watch/providers,credits'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None