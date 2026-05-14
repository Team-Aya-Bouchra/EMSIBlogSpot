from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from articles.models import Article
from .models import Comment

@login_required
def add_comment(request, article_id):
    if request.method == 'POST':
        # Block Admins mathematically
        if hasattr(request.user, 'adminuser') or request.user.is_superuser:
            raise PermissionDenied("Admins are strictly forbidden from commenting.")
            
        article = get_object_or_404(Article, id=article_id)
        content = request.POST.get('content')
        
        if content:
            Comment.objects.create(
                article=article,
                user=request.user,
                content=content
            )
            
    # Redirect back to the beautiful article detail page
    return redirect('article_detail', slug=article.slug)

@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        c = get_object_or_404(Comment, id=comment_id)
        is_owner = c.user == request.user
        is_author = hasattr(request.user, 'author') and c.article.author == request.user.author
        is_admin = hasattr(request.user, 'adminuser') or request.user.is_superuser
        
        if not (is_owner or is_author or is_admin):
            raise PermissionDenied("You do not have permission to delete this comment.")
            
        if is_admin and not is_owner:
            c.content = "[deleted by admin/moderator]"
            c.save()
        else:
            c.delete()
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def author_like_comment(request, comment_id):
    if request.method == 'POST':
        c = get_object_or_404(Comment, id=comment_id)
        if not (hasattr(request.user, 'author') and c.article.author == request.user.author):
            raise PermissionDenied("Only the Article Author can spotlight a comment.")
        c.is_liked_by_author = not c.is_liked_by_author
        c.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

from django.contrib import messages

@login_required
def edit_comment(request, comment_id):
    if request.method == 'POST':
        c = get_object_or_404(Comment, id=comment_id)
        if c.user != request.user:
            raise PermissionDenied("You can only edit your own comments.")
        
        new_content = request.POST.get('content')
        if new_content:
            c.content = new_content
            c.save()
            messages.success(request, 'Comment edited.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
