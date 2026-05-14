from django.views.generic import ListView, DetailView, TemplateView
from .models import Article

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

class HeroView(TemplateView):
    template_name = 'hero.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('feed')
        return super().get(request, *args, **kwargs)

class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if hasattr(request.user, 'author'):
                return redirect('dashboard')
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Article.objects.filter(status='Publié').order_by('-created_at')
        tab = self.request.GET.get('tab', 'general')
        if tab == 'following' and self.request.user.is_authenticated and hasattr(self.request.user, 'reader'):
            followed_authors = [f.author for f in self.request.user.reader.following.all()]
            queryset = queryset.filter(author__in=followed_authors)
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tab'] = self.request.GET.get('tab', 'general')
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.is_authenticated:
            if hasattr(request.user, 'author') and self.object.author != request.user.author:
                raise PermissionDenied("Authors are strictly siloed and cannot view competing articles.")
        
        context = self.get_context_data(object=self.object)
        
        # Add interaction states
        if request.user.is_authenticated and hasattr(request.user, 'reader'):
            from interactions.models import ArticleLike, Follow
            context['is_liked'] = ArticleLike.objects.filter(reader=request.user.reader, article=self.object).exists()
            context['is_following'] = Follow.objects.filter(reader=request.user.reader, author=self.object.author).exists()
            
        sort = request.GET.get('sort', 'new')
        if sort == 'old':
            context['comments'] = self.object.comments.all().order_by('created_at')
        else:
            context['comments'] = self.object.comments.all().order_by('-created_at')
        context['sort_by'] = sort
            
        return self.render_to_response(context)

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect

@login_required
def moderator_delete_article(request, article_id):
    if request.method == 'POST':
        if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
            raise PermissionDenied("Only AdminUsers can globally delete articles.")
        article = get_object_or_404(Article, id=article_id)
        article.delete()
    return redirect('dashboard')

@login_required
def author_delete_article(request, article_id):
    if request.method == 'POST':
        if not hasattr(request.user, 'author'):
            raise PermissionDenied("Only Authors can delete their own articles.")
        article = get_object_or_404(Article, id=article_id, author=request.user.author)
        article.delete()
    return redirect('dashboard')

from django.contrib import messages
from tags.models import Tag

@login_required
def author_edit_article(request, article_id):
    if not hasattr(request.user, 'author'):
        raise PermissionDenied("Only Authors can edit their own articles.")
        
    article = get_object_or_404(Article, id=article_id, author=request.user.author)
    
    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        cover_image = request.FILES.get('cover_image')
        
        if cover_image:
            article.cover_image = cover_image
            
        tags_raw = request.POST.get('tags', '')
        if tags_raw:
            try:
                import json
                tags_data = json.loads(tags_raw)
                tag_names = [t.get('value').strip() for t in tags_data if isinstance(t, dict) and t.get('value')]
            except Exception:
                tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
            
            tag_objs = []
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                tag_objs.append(tag)
            article.tags.set(tag_objs)
            
        article.save()
        messages.success(request, 'Article updated successfully.')
        return redirect('dashboard')
        
    tags_string = ", ".join([tag.name for tag in article.tags.all()])
    context = {
        'article': article, 
        'tags_string': tags_string,
        'all_tags': list(Tag.objects.values_list('name', flat=True))
    }
    return render(request, 'articles/edit_article.html', context)

from django.db.models import Q
from django.shortcuts import render

def explore_articles(request):
    if request.user.is_authenticated and hasattr(request.user, 'author'):
        return redirect('dashboard')
        
    query = request.GET.get('q', '')
    articles = Article.objects.filter(status='Publié').order_by('-created_at')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
        
    tags = Tag.objects.all()[:15]
    
    return render(request, 'articles/explore.html', {
        'articles': articles, 
        'query': query, 
        'tags': tags
    })
