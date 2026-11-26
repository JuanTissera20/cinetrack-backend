from django.db import models
from django.contrib.auth.models import User

class MediaItem(models.Model):
    TYPE_CHOICES = (
        ('movie', 'Película'),
        ('tv', 'Serie'),
    )
    
    tmdb_id = models.IntegerField(unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    release_date = models.CharField(max_length=20, null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    vote_average = models.FloatField(default=0.0)
    genres = models.CharField(max_length=255, null=True, blank=True) # Guardado como string ej: "Acción, Drama"

    def __str__(self):
        return f"{self.title} ({self.media_type})"


class UserMedia(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Quiero ver'),
        ('watching', 'Viendo actualmente'),
        ('finished', 'Finalizada'),
        ('dropped', 'Abandonada'),
        ('rewatch', 'Rewatch pendiente'),
    )
    
    PRIORITY_CHOICES = (
        ('high', 'Alta 🔥'),
        ('medium', 'Media 🟡'),
        ('low', 'Baja ⚪'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_backlog')
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Datos de consumo personal
    personal_rating = models.IntegerField(null=True, blank=True) # 1 a 10
    review = models.TextField(null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    watched_date = models.DateField(null=True, blank=True)
    
    # Seguimiento específico de series
    current_season = models.IntegerField(default=1)
    current_episode = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'media_item') # No duplicar la misma película en el backlog del usuario

    def __str__(self):
        return f"{self.user.username} - {self.media_item.title} [{self.status}]"
