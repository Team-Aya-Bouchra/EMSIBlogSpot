from django.urls import path
from .views import HeroView, ArticleListView, ArticleDetailView, moderator_delete_article, author_delete_article, author_edit_article, explore_articles

urlpatterns = [
    path('', HeroView.as_view(), name='hero'),
    path('home/', ArticleListView.as_view(), name='feed'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('article/<int:article_id>/delete/', moderator_delete_article, name='moderator_delete_article'),
    path('article/<int:article_id>/author_delete/', author_delete_article, name='author_delete_article'),
    path('article/<int:article_id>/edit/', author_edit_article, name='author_edit_article'),
    path('explore/', explore_articles, name='explore_articles'),
]
