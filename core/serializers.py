from rest_framework import serializers
from .models import MediaItem, UserMedia

class MediaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaItem
        fields = '__all__'


class UserMediaSerializer(serializers.ModelSerializer):
    media_item = MediaItemSerializer(read_only=True)
    # Campos que enviamos al agregar desde la búsqueda de TMDb
    tmdb_id = serializers.IntegerField(write_only=True)
    title = serializers.CharField(write_only=True)
    media_type = serializers.ChoiceField(choices=MediaItem.TYPE_CHOICES, write_only=True)
    release_date = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    poster_path = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    overview = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    vote_average = serializers.FloatField(write_only=True, required=False, default=0.0)

    class Meta:
        model = UserMedia
        fields = [
            'id', 'media_item', 'tmdb_id', 'title', 'media_type',
            'release_date', 'poster_path', 'overview', 'vote_average',
            'status', 'priority', 'personal_rating', 'review',
            'is_favorite', 'watched_date', 'current_season', 'current_episode',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        
        # Extraemos los datos técnicos de TMDb para cachear el MediaItem
        media_data = {
            'title': validated_data.pop('title'),
            'media_type': validated_data.pop('media_type'),
            'release_date': validated_data.pop('release_date', None),
            'poster_path': validated_data.pop('poster_path', None),
            'overview': validated_data.pop('overview', None),
            'vote_average': validated_data.pop('vote_average', 0.0),
        }
        tmdb_id = validated_data.pop('tmdb_id')

        media_item, _ = MediaItem.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults=media_data
        )

        # Creamos o actualizamos la entrada en el backlog del usuario
        user_media, _ = UserMedia.objects.update_or_create(
            user=user,
            media_item=media_item,
            defaults=validated_data
        )
        return user_media