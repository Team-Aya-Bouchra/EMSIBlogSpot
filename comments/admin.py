from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at', 'is_liked_by_author')
    list_filter = ('created_at', 'is_liked_by_author')
    search_fields = ('content',)
