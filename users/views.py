from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Author, Reader
from django.core.exceptions import PermissionDenied

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role_select = request.POST.get('role') # 'Author' or 'Reader'
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Super simple check
        if Author.objects.filter(username=username).exists() or Reader.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('register')
            
        if role_select == 'Author':
            user = Author.objects.create_user(username=username, email=email, password=password)
        else:
            user = Reader.objects.create_user(username=username, email=email, password=password)
            
        user.first_name = first_name
        user.last_name = last_name
        user.save()
            
        login(request, user)
        return redirect('dashboard')
        
    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            if user.is_banned:
                messages.error(request, "Your account has been disabled by the admins until another notice.")
                return redirect('login')
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            from .models import User
            try_user = User.objects.filter(username=u).first()
            if try_user and try_user.check_password(p) and not try_user.is_active:
                messages.error(request, "Your account has been disabled by the admins until another notice.")
            else:
                messages.error(request, 'Invalid credentials.')
            
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('feed')

import urllib.parse
from django.conf import settings
import requests
import uuid

def google_login(request):
    role = request.GET.get('role')
    if role in ['Author', 'Reader']:
        request.session['oauth_role'] = role
        
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(url)

def google_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google authentication failed.')
        return redirect('login')
        
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        if not response.ok:
            messages.error(request, 'Failed to obtain access token from Google.')
            return redirect('login')
            
        access_token = response.json().get('access_token')
        
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)
        
        if not user_info_response.ok:
            messages.error(request, 'Failed to fetch user information from Google.')
            return redirect('login')
            
        user_info = user_info_response.json()
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        
        from .models import User, Reader, Author
        user = User.objects.filter(email=email).first()
        
        if user:
            if user.is_banned or not user.is_active:
                messages.error(request, "Your account has been disabled by the admins until another notice.")
                return redirect('login')
            login(request, user)
            
            # Clean up session just in case
            if 'oauth_role' in request.session:
                del request.session['oauth_role']
                
            return redirect('dashboard')
        else:
            # Create new user based on requested role
            role = request.session.get('oauth_role', 'Reader')
            
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            random_password = str(uuid.uuid4())
            
            if role == 'Author':
                new_user = Author.objects.create_user(username=username, email=email, password=random_password)
            else:
                new_user = Reader.objects.create_user(username=username, email=email, password=random_password)
                
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()
            
            # Clean up session
            if 'oauth_role' in request.session:
                del request.session['oauth_role']
                
            login(request, new_user)
            return redirect('dashboard')
            
    except Exception as e:
        messages.error(request, 'An error occurred during Google authentication.')
        return redirect('login')

from django.contrib.auth.decorators import login_required
from articles.models import Article

@login_required
def dashboard_router(request):
    user = request.user
    
    if hasattr(user, 'adminuser') or user.is_superuser:
        return redirect('custom_admin_dashboard')
        
    elif hasattr(user, 'author'):
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            cover_image = request.FILES.get('cover_image')
            tags_raw = request.POST.get('tags', '')
            
            import uuid
            from django.utils.text import slugify
            from tags.models import Tag
            
            slug = slugify(title) + "-" + str(uuid.uuid4())[:8]
            article = Article.objects.create(
                author=user.author,
                title=title,
                content=content,
                slug=slug,
                status='Publié'
            )
            
            if cover_image:
                article.cover_image = cover_image
                article.save()
                
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
                
            messages.success(request, 'Article published successfully!')
            return redirect('dashboard')
            
        from tags.models import Tag
        
        sort_by = request.GET.get('sort', 'recent')
        if sort_by == 'popular':
            from django.db.models import Count
            articles = user.author.articles.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
        elif sort_by == 'oldest':
            articles = user.author.articles.all().order_by('created_at')
        else:
            articles = user.author.articles.all().order_by('-created_at')
            
        comments = user.comments.all().order_by('-created_at')
        total_likes = sum(a.likes.count() for a in user.author.articles.all())
        
        context = {
            'all_tags': list(Tag.objects.values_list('name', flat=True)),
            'total_likes': total_likes,
            'followers': [f.reader for f in user.author.followers.all().order_by('-created_at')],
            'articles': articles,
            'comments': comments,
            'sort_by': sort_by,
        }
        return render(request, 'users/dashboards/author_dashboard.html', context)
        
    elif hasattr(user, 'reader'):
        context = {
            'liked_articles': [like.article for like in user.reader.article_likes.all().order_by('-created_at')],
            'followed_authors': [f.author for f in user.reader.following.all().order_by('-created_at')],
            'comments': user.comments.all().order_by('-created_at')
        }
        return render(request, 'users/dashboards/reader_dashboard.html', context)
        
    else:
        return redirect('/admin/')

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import User

@login_required
def moderator_ban_user(request):
    if request.method == 'POST':
        if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
            raise PermissionDenied("Only AdminUsers can ban accounts.")
            
        target_username = request.POST.get('target_username')
        reason = request.POST.get('reason')
        
        # Don't let an admin ban themselves or another admin
        target_user = get_object_or_404(User, username=target_username)
        if hasattr(target_user, 'adminuser') or target_user.is_superuser:
            messages.error(request, 'Cannot ban other administrators.')
            return redirect('dashboard')
            
        target_user.is_banned = True
        target_user.ban_reason = reason
        target_user.save()
        
        messages.success(request, f'User {target_username} has been permanently banned.')
    return redirect('dashboard')

def author_profile(request, username):
    # Public view for Readers and Unauthentified users to see an author's articles
    author = get_object_or_404(Author, username=username)
    
    sort_by = request.GET.get('sort', 'recent')
    if sort_by == 'oldest':
        articles = author.articles.filter(status='Publié').order_by('created_at')
    elif sort_by == 'popular':
        from django.db.models import Count
        articles = author.articles.filter(status='Publié').annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    else:
        articles = author.articles.filter(status='Publié').order_by('-created_at')
        
    context = {
        'profile_author': author,
        'articles': articles,
        'sort_by': sort_by,
    }
    
    if request.user.is_authenticated and hasattr(request.user, 'reader'):
        from interactions.models import Follow
        context['is_following'] = Follow.objects.filter(reader=request.user.reader, author=author).exists()
        
    return render(request, 'users/author_profile.html', context)

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('feed')
    return redirect('update_profile')

@login_required
def request_author_promotion(request):
    if request.method == 'POST' and hasattr(request.user, 'reader'):
        request.user.reader.wants_to_be_author = True
        request.user.reader.save()
        messages.success(request, 'Your request to become an Author has been submitted to the platform administrators!')
    return redirect('dashboard')

@login_required
def cancel_author_promotion(request):
    if request.method == 'POST' and hasattr(request.user, 'reader'):
        request.user.reader.wants_to_be_author = False
        request.user.reader.save()
        messages.success(request, 'Your promotion request has been securely cancelled.')
    return redirect('dashboard')

@login_required
def promote_user(request, username):
    if request.method == 'POST':
        if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
            raise PermissionDenied("Only AdminUsers can promote accounts.")
            
        target_user = get_object_or_404(User, username=username)
        if hasattr(target_user, 'reader'):
            reader_obj = target_user.reader
            bio = reader_obj.bio
            avatar = reader_obj.avatar
            
            # Delete reader child row but keep the parent User row
            reader_obj.delete(keep_parents=True)
            
            # Create the author child row mapped to the parent User
            author = Author(
                user_ptr_id=target_user.id,
                bio=bio,
                avatar=avatar
            )
            author.__dict__.update(target_user.__dict__)
            author.save()
            messages.success(request, f'User {username} has been successfully promoted to Author!')
            
    return redirect('dashboard')

@login_required
def update_profile(request):
    user = request.user
    user_profile = getattr(user, 'author', getattr(user, 'reader', None))
    
    if request.method == 'POST':
        if not user_profile and not user.is_superuser:
            raise PermissionDenied("Only Readers and Authors can update generic profiles.")
            
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        new_username = request.POST.get('username')
        
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Profile properties (Bio + Avatar)
        if user_profile:
            user_profile.bio = request.POST.get('bio', '')
            avatar = request.FILES.get('avatar')
            if avatar:
                user_profile.avatar = avatar
            user_profile.save()
            
        # Core Auth Properties
        user.first_name = first_name
        user.last_name = last_name
        
        if new_username and new_username != user.username:
            from .models import User
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'That username is already taken.')
                return redirect('update_profile')
            user.username = new_username
            
        # Password Verification Pipeline
        if current_password or new_password or confirm_password:
            if not user.check_password(current_password):
                messages.error(request, 'Incorrect current password.')
                return redirect('update_profile')
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
                return redirect('update_profile')
            if new_password:
                user.set_password(new_password)
                
        user.save()
        
        if new_password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user) # Prevents user disconnect
            
        messages.success(request, 'Your configuration has been updated successfully.')
        return redirect('dashboard')
        
    return render(request, 'users/update_profile.html', {'profile': user_profile})

import json
import os
from datetime import datetime

@login_required
def custom_admin_dashboard(request):
    user = request.user
    if not (hasattr(user, 'adminuser') or user.is_superuser):
        raise PermissionDenied("Only AdminUsers can access the admin portal.")
        
    reports_file = os.path.join(settings.BASE_DIR, 'reports.json')
    reports = []
    if os.path.exists(reports_file):
        try:
            with open(reports_file, 'r', encoding='utf-8') as f:
                reports = json.load(f)
        except Exception:
            pass

    from interactions.models import ArticleLike
    from articles.models import Article
    from .models import User, Reader
    
    context = {
        'total_users': User.objects.count(),
        'total_articles': Article.objects.count(),
        'total_likes': ArticleLike.objects.count(),
        'articles': Article.objects.all().order_by('-created_at'),
        'pending_authors': Reader.objects.filter(wants_to_be_author=True),
        'all_users': User.objects.exclude(id=request.user.id).exclude(username='').order_by('-date_joined'),
        'reports': sorted(reports, key=lambda x: x.get('date', ''), reverse=True)
    }
    return render(request, 'users/dashboards/admin_dashboard.html', context)

@login_required
def toggle_user_status(request, username):
    if request.method == 'POST':
        if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
            raise PermissionDenied("Only AdminUsers can modify account statuses.")
            
        target_user = get_object_or_404(User, username=username)
        if hasattr(target_user, 'adminuser') or target_user.is_superuser:
            messages.error(request, 'Cannot modify other administrators.')
            return redirect('custom_admin_dashboard')
            
        # Toggle active status
        target_user.is_active = not target_user.is_active
        target_user.save()
        
        status = "enabled" if target_user.is_active else "disabled"
        messages.success(request, f'User {username} has been {status}.')
        
    return redirect('custom_admin_dashboard')

@login_required
def submit_report(request):
    if request.method == 'POST':
        reason = request.POST.get('reason')
        target_url = request.POST.get('target_url')
        
        reports_file = os.path.join(settings.BASE_DIR, 'reports.json')
        reports = []
        if os.path.exists(reports_file):
            try:
                with open(reports_file, 'r', encoding='utf-8') as f:
                    reports = json.load(f)
            except Exception:
                pass
                
        reports.append({
            'reporter': request.user.username,
            'target_url': target_url,
            'reason': reason,
            'date': datetime.now().isoformat()
        })
        
        with open(reports_file, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=4)
            
        messages.success(request, 'Thank you. Your report has been submitted to the administration.')
        return redirect(request.META.get('HTTP_REFERER', 'feed'))
    return redirect('feed')

from django.db.models import Q

@login_required
def admin_readers_list(request):
    if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
        raise PermissionDenied()
        
    query = request.GET.get('q', '')
    readers = Reader.objects.exclude(username='').order_by('-date_joined')
    if query:
        readers = readers.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        
    return render(request, 'users/dashboards/admin_readers.html', {'readers': readers, 'query': query})

@login_required
def admin_authors_list(request):
    if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
        raise PermissionDenied()
        
    query = request.GET.get('q', '')
    authors = Author.objects.exclude(username='').order_by('-date_joined')
    if query:
        authors = authors.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))
        
    return render(request, 'users/dashboards/admin_authors.html', {'authors': authors, 'query': query})

@login_required
def admin_articles_list(request):
    if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
        raise PermissionDenied()
        
    query = request.GET.get('q', '')
    author_filter = request.GET.get('author', '')
    
    from articles.models import Article
    articles = Article.objects.exclude(author__username='').order_by('-created_at')
    
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(content__icontains=query))
        
    if author_filter:
        articles = articles.filter(author__username__icontains=author_filter)
            
    return render(request, 'users/dashboards/admin_articles.html', {
        'articles': articles, 
        'query': query,
        'author_filter': author_filter
    })

@login_required
def admin_user_detail(request, username):
    if not (hasattr(request.user, 'adminuser') or request.user.is_superuser):
        raise PermissionDenied()
        
    target_user = get_object_or_404(User, username=username)
    context = {'target_user': target_user, 'comments': target_user.comments.all().order_by('-created_at')}
    
    if hasattr(target_user, 'author'):
        context['role'] = 'Author'
        context['followers'] = target_user.author.followers.all()
        context['articles'] = target_user.author.articles.all().order_by('-created_at')
    elif hasattr(target_user, 'reader'):
        context['role'] = 'Reader'
        context['followings'] = target_user.reader.following.all()
    else:
        context['role'] = 'Admin / Staff'
        
    return render(request, 'users/dashboards/admin_user_detail.html', context)

from django.http import JsonResponse
from django.utils import timezone

@login_required
def mark_notifications_read(request):
    if request.method == 'POST':
        request.session['last_notification_check'] = timezone.now().isoformat()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def notifications_view(request):
    if not hasattr(request.user, 'author'):
        return redirect('dashboard')
        
    return render(request, 'users/notifications.html')
