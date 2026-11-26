from django.contrib import admin
from .models import MediaItem, UserMedia

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('tmdb_id', 'title', 'media_type', 'release_date', 'vote_average')
    search_fields = ('title', 'tmdb_id')
    list_filter = ('media_type',)

@admin.register(UserMedia)
class UserMediaAdmin(admin.ModelAdmin):
    list_display = ('user', 'media_item', 'status', 'priority', 'personal_rating', 'updated_at')
    list_filter = ('status', 'priority', 'is_favorite')
    search_fields = ('user__username', 'media_item__title')
# Register your models here.
