from django.contrib import admin
from .models import ArticleLike, Follow

@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ('reader', 'article', 'created_at')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('reader', 'author', 'created_at')
