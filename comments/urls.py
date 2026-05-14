from django.urls import path
from .views import add_comment, delete_comment, author_like_comment, edit_comment

urlpatterns = [
    path('<int:article_id>/add/', add_comment, name='add_comment'),
    path('<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('<int:comment_id>/author_like/', author_like_comment, name='author_like_comment'),
]
