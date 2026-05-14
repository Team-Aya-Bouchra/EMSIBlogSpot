from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from articles.models import Article
from interactions.models import ArticleLike, Follow
from users.models import Author

@login_required
def toggle_like(request, article_id):
    if request.method == 'POST':
        # Safely enforce the reader requirement
        if not hasattr(request.user, 'reader'):
            raise PermissionDenied("Only Readers are allowed to like articles.")
            
        article = get_object_or_404(Article, id=article_id)
        
        # Toggle functionality
        like, created = ArticleLike.objects.get_or_create(
            reader=request.user.reader,
            article=article
        )
        if not created:
            like.delete()
            
    return redirect('article_detail', slug=article.slug)

@login_required
def follow_author(request, author_id):
    if request.method == 'POST':
        if not hasattr(request.user, 'reader'):
            raise PermissionDenied("Only Readers are allowed to follow Authors.")
            
        author = get_object_or_404(Author, id=author_id)
        
        follow, created = Follow.objects.get_or_create(
            reader=request.user.reader,
            author=author
        )
        if not created:
            follow.delete()
            
    # Redirect back to where they came from (HTTP_REFERER)
    return redirect(request.META.get('HTTP_REFERER', '/'))
